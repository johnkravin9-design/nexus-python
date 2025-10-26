import eventlet; eventlet.monkey_patch()
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexus-master-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nexus_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['PROFILE_PICTURE_SIZE'] = (200, 200)
app.config['POST_IMAGE_SIZE'] = (800, 600)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    profile_picture = db.Column(db.String(200), default='default.png')
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_profile_picture_url(self):
        if self.profile_picture and self.profile_picture != 'default.png':
            return f"/static/{self.profile_picture}"
        else:
            return "/static/uploads/profile_pictures/default.png"

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    follower = db.relationship('User', foreign_keys=[follower_id], backref='following')
    following = db.relationship('User', foreign_keys=[following_id], backref='followers')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('posts', lazy=True, order_by='Post.created_at.desc()'))
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('likes', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    chat = db.relationship('Chat', backref=db.backref('messages', lazy=True, order_by='Message.created_at.asc()'))
    sender = db.relationship('User', backref=db.backref('sent_messages', lazy=True))

User.chats = db.relationship('Chat', secondary='chat_participant', backref=db.backref('participants', lazy=True))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_profile_picture(file, username):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{username}_{int(datetime.utcnow().timestamp())}.{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pictures', unique_filename)
        image = Image.open(file)
        image = image.convert('RGB')
        image.thumbnail(app.config['PROFILE_PICTURE_SIZE'], Image.Resampling.LANCZOS)
        image.save(filepath, 'JPEG', quality=85)
        static_path = os.path.join('static', 'uploads', 'profile_pictures', unique_filename)
        image.save(static_path, 'JPEG', quality=85)
        return f"uploads/profile_pictures/{unique_filename}"
    return None

def save_post_image(file, username):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"post_{username}_{int(datetime.utcnow().timestamp())}.{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'post_images', unique_filename)
        image = Image.open(file)
        image = image.convert('RGB')
        image.thumbnail(app.config['POST_IMAGE_SIZE'], Image.Resampling.LANCZOS)
        image.save(filepath, 'JPEG', quality=85)
        static_path = os.path.join('static', 'uploads', 'post_images', unique_filename)
        image.save(static_path, 'JPEG', quality=85)
        return f"uploads/post_images/{unique_filename}"
    return None

def delete_old_profile_picture(user):
    if user.profile_picture and user.profile_picture != 'default.png':
        old_path = user.profile_picture
        if os.path.exists(old_path):
            os.remove(old_path)
        static_path = os.path.join('static', old_path)
        if os.path.exists(static_path):
            os.remove(static_path)

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        identifier = data.get('identifier')
        password = data.get('password')
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True, 'message': 'Login successful!'})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials!'})
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'success': False, 'message': 'Username or email already exists!'})
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Account created successfully!'})

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    return render_template('dashboard.html', username=session['username'], user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if request.method == 'POST':
        user.full_name = request.form.get('full_name', '')
        user.bio = request.form.get('bio', '')
        user.location = request.form.get('location', '')
        user.website = request.form.get('website', '')
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=user)

@app.route('/profile/<username>')
def public_profile(username):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=username).first_or_404()
    is_own_profile = user.id == session['user_id']
    is_following = Connection.query.filter_by(follower_id=session['user_id'], following_id=user.id).first() is not None
    return render_template('public_profile.html', user=user, is_own_profile=is_own_profile, is_following=is_following)

@app.route('/follow/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    if session['user_id'] == user_id:
        return jsonify({'success': False, 'message': 'Cannot follow yourself'})
    existing_connection = Connection.query.filter_by(follower_id=session['user_id'], following_id=user_id).first()
    if not existing_connection:
        new_connection = Connection(follower_id=session['user_id'], following_id=user_id)
        db.session.add(new_connection)
        db.session.commit()
    return jsonify({'success': True, 'message': 'Followed successfully'})

@app.route('/unfollow/<int:user_id>', methods=['POST'])
def unfollow_user(user_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    connection = Connection.query.filter_by(follower_id=session['user_id'], following_id=user_id).first()
    if connection:
        db.session.delete(connection)
        db.session.commit()
    return jsonify({'success': True, 'message': 'Unfollowed successfully'})

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        image_file = request.files.get('post_image')
        if not content and not image_file:
            return render_template('create_post.html', error='Post must contain text or an image')
        image_url = None
        if image_file and image_file.filename:
            user = db.session.get(User, session['user_id'])
            image_url = save_post_image(image_file, user.username)
            if not image_url:
                return render_template('create_post.html', error='Invalid image file')
        new_post = Post(content=content, image_url=image_url, user_id=session['user_id'])
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('feed'))
    return render_template('create_post.html')

@app.route('/feed')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user = db.session.get(User, session['user_id'])
    feed_type = request.args.get('type', 'public')
    if feed_type == 'following':
        following_ids = [conn.following_id for conn in current_user.following]
        following_ids.append(current_user.id)
        posts = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.created_at.desc()).all()
        feed_title = "Following"
    else:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        feed_title = "Public Feed"
    return render_template('feed.html', posts=posts, feed_title=feed_title, feed_type=feed_type, current_user=current_user, username=session['username'])

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    existing_like = Like.query.filter_by(user_id=session['user_id'], post_id=post_id).first()
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'success': True, 'liked': False, 'likes_count': Like.query.filter_by(post_id=post_id).count()})
    else:
        new_like = Like(user_id=session['user_id'], post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
        return jsonify({'success': True, 'liked': True, 'likes_count': Like.query.filter_by(post_id=post_id).count()})

@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    content = request.json.get('content', '').strip()
    if not content:
        return jsonify({'success': False, 'message': 'Comment cannot be empty'})
    new_comment = Comment(content=content, user_id=session['user_id'], post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'success': True, 'comment': {'content': content, 'username': session['username'], 'created_at': new_comment.created_at.strftime('%b %d, %Y')}})

@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    if 'profile_picture' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'})
    file = request.files['profile_picture']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    user = db.session.get(User, session['user_id'])
    if file and allowed_file(file.filename):
        delete_old_profile_picture(user)
        filename = save_profile_picture(file, user.username)
        if filename:
            user.profile_picture = filename
            db.session.commit()
            return jsonify({'success': True, 'message': 'Profile picture updated successfully!', 'image_url': user.get_profile_picture_url()})
    return jsonify({'success': False, 'message': 'Invalid file type'})

@app.route('/upload_post_image', methods=['POST'])
def upload_post_image():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    if 'post_image' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'})
    file = request.files['post_image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    user = db.session.get(User, session['user_id'])
    if file and allowed_file(file.filename):
        filename = save_post_image(file, user.username)
        if filename:
            return jsonify({'success': True, 'message': 'Image uploaded successfully!', 'image_url': f"/static/{filename}"})
    return jsonify({'success': False, 'message': 'Invalid file type'})

# Search Routes
@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    query = request.args.get('q', '').strip()
    users = []
    
    if query:
        # Search for users by username, full name, or bio
        users = User.query.filter(
            (User.username.ilike(f'%{query}%')) |
            (User.full_name.ilike(f'%{query}%')) |
            (User.bio.ilike(f'%{query}%'))
        ).all()
    
    return render_template('search.html', users=users, query=query)

@app.route('/api/search/users')
def api_search_users():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'success': True, 'users': []})
    
    users = User.query.filter(
        (User.username.ilike(f'%{query}%')) |
        (User.full_name.ilike(f'%{query}%'))
    ).limit(10).all()
    
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name or user.username,
            'bio': user.bio,
            'profile_picture_url': user.get_profile_picture_url(),
            'is_following': Connection.query.filter_by(
                follower_id=session['user_id'], 
                following_id=user.id
            ).first() is not None
        })
    
    return jsonify({'success': True, 'users': users_data})

@app.route('/discover')
def discover_users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get current user
    current_user = db.session.get(User, session['user_id'])
    
    # Get users that the current user is NOT following (excluding themselves)
    following_ids = [conn.following_id for conn in current_user.following]
    following_ids.append(current_user.id)  # Exclude self
    
    # Get suggested users (not followed yet)
    suggested_users = User.query.filter(
        User.id.notin_(following_ids)
    ).order_by(User.created_at.desc()).limit(50).all()
    
    # If not enough suggestions, get random users
    if len(suggested_users) < 5:
        suggested_users = User.query.filter(
            User.id != current_user.id
        ).order_by(db.func.random()).limit(20).all()
    
    return render_template('discover.html', 
                         suggested_users=suggested_users, 
                         current_user=current_user)

@app.route('/messages')
def messages():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    return render_template('messages.html', user=user)

@app.route('/chat/<int:user_id>')
def start_chat(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    target_user = db.session.get(User, user_id)
    if not target_user:
        return redirect(url_for('messages'))
    existing_chat = None
    current_user = db.session.get(User, session['user_id'])
    for chat in current_user.chats:
        if len(chat.participants) == 2 and target_user in chat.participants:
            existing_chat = chat
            break
    if not existing_chat:
        new_chat = Chat()
        new_chat.participants.append(current_user)
        new_chat.participants.append(target_user)
        db.session.add(new_chat)
        db.session.commit()
        existing_chat = new_chat
    return render_template('chat.html', chat=existing_chat, target_user=target_user, user=current_user)

@app.route('/api/chats')
def get_chats():
    if 'user_id' not in session:
        return jsonify({'success': False})
    user = db.session.get(User, session['user_id'])
    chats_data = []
    for chat in user.chats:
        other_user = next((u for u in chat.participants if u.id != user.id), None)
        if other_user:
            last_message = chat.messages[-1] if chat.messages else None
            chats_data.append({
                'id': chat.id,
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username,
                    'full_name': other_user.full_name or other_user.username
                },
                'last_message': {
                    'content': last_message.content if last_message else 'No messages yet',
                    'created_at': last_message.created_at.isoformat() if last_message else None,
                    'is_own': last_message.sender_id == user.id if last_message else False
                },
                'unread_count': len([m for m in chat.messages if m.read_at is None and m.sender_id != user.id])
            })
    return jsonify({'success': True, 'chats': chats_data})

# ===== ADMIN ROUTES =====
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = db.session.get(User, session['user_id'])
        if not user.is_admin:
            return "Access denied: Admin privileges required", 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Get platform statistics
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_likes = Like.query.count()
    total_comments = Comment.query.count()
    total_chats = Chat.query.count()
    
    # Get recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    # Get user growth data (last 7 days)
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = User.query.filter(User.created_at >= week_ago).count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_posts=total_posts,
                         total_likes=total_likes,
                         total_comments=total_comments,
                         total_chats=total_chats,
                         recent_users=recent_users,
                         recent_posts=recent_posts,
                         new_users_week=new_users_week)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/posts')
@admin_required
def admin_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts)

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    # User growth data
    from datetime import timedelta
    today = datetime.utcnow().date()
    dates = []
    user_counts = []
    post_counts = []
    
    for i in range(7, -1, -1):
        date = today - timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        user_count = User.query.filter(
            db.func.date(User.created_at) <= date
        ).count()
        post_count = Post.query.filter(
            db.func.date(Post.created_at) <= date
        ).count()
        user_counts.append(user_count)
        post_counts.append(post_count)
    
    # Most active users
    active_users = User.query.all()
    active_users = sorted(active_users, key=lambda u: len(u.posts) + len(u.comments), reverse=True)[:10]
    
    return render_template('admin/analytics.html',
                         dates=dates,
                         user_counts=user_counts,
                         post_counts=post_counts,
                         active_users=active_users)

@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = db.session.get(User, user_id)
    if user:
        user.is_admin = not user.is_admin
        db.session.commit()
        return jsonify({'success': True, 'is_admin': user.is_admin})
    return jsonify({'success': False})

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        return jsonify({'success': False, 'message': 'Cannot delete your own account'})
    
    user = db.session.get(User, user_id)
    if user:
        # Delete user's posts, likes, comments, etc.
        Post.query.filter_by(user_id=user_id).delete()
        Like.query.filter_by(user_id=user_id).delete()
        Comment.query.filter_by(user_id=user_id).delete()
        
        # Delete user's chat participation
        ChatParticipant.query.filter_by(user_id=user_id).delete()
        
        # Delete user's connections
        Connection.query.filter(
            (Connection.follower_id == user_id) | (Connection.following_id == user_id)
        ).delete()
        
        # Finally delete the user
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/admin/delete_post/<int:post_id>', methods=['POST'])
@admin_required
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if post:
        # Delete associated likes and comments
        Like.query.filter_by(post_id=post_id).delete()
        Comment.query.filter_by(post_id=post_id).delete()
        
        db.session.delete(post)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/admin/make_admin')
@admin_required
def make_admin():
    # Make first user admin (for initial setup)
    first_user = User.query.first()
    if first_user:
        first_user.is_admin = True
        db.session.commit()
        return "Admin privileges granted to first user"
    return "No users found"

@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        join_room(f"user_{session['user_id']}")
        print(f"User {session['user_id']} connected to chat")

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        leave_room(f"user_{session['user_id']}")
        print(f"User {session['user_id']} disconnected")

@socketio.on('join_chat')
def handle_join_chat(data):
    chat_id = data['chat_id']
    join_room(f"chat_{chat_id}")
    print(f"User {session['user_id']} joined chat {chat_id}")

@socketio.on('send_message')
def handle_send_message(data):
    if 'user_id' not in session:
        return
    chat_id = data['chat_id']
    content = data['content'].strip()
    if not content:
        return
    new_message = Message(content=content, chat_id=chat_id, sender_id=session['user_id'])
    chat = db.session.get(Chat, chat_id)
    chat.last_message_at = datetime.utcnow()
    db.session.add(new_message)
    db.session.commit()
    sender = db.session.get(User, session['user_id'])
    message_data = {
        'id': new_message.id,
        'content': new_message.content,
        'sender_id': new_message.sender_id,
        'sender_username': sender.username,
        'created_at': new_message.created_at.isoformat(),
        'chat_id': chat_id
    }
    emit('new_message', message_data, room=f"chat_{chat_id}")
    for participant in chat.participants:
        if participant.id != session['user_id']:
            emit('message_notification', {'chat_id': chat_id, 'message': message_data, 'sender': sender.username}, room=f"user_{participant.id}")

@socketio.on('mark_as_read')
def handle_mark_as_read(data):
    if 'user_id' not in session:
        return
    chat_id = data['chat_id']
    chat = db.session.get(Chat, chat_id)
    for message in chat.messages:
        if message.sender_id != session['user_id'] and message.read_at is None:
            message.read_at = datetime.utcnow()
    db.session.commit()

def init_db():
    """Initialize the database with sample data"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_sample_data()
        print("🔄 Creating fresh master database...")

if __name__ == '__main__':
    # init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
