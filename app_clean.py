from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexus-clean-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nexus_clean.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ===== CLEAN DATABASE MODELS =====

# User Model (ONLY ONE DEFINITION)
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
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Post Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

# Like Model
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('likes', lazy=True))

# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

# Connection Model (Follow System)
class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    follower = db.relationship('User', foreign_keys=[follower_id], backref='following')
    following = db.relationship('User', foreign_keys=[following_id], backref='followers')

# Chat Models (Simplified - No complex relationships for now)
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)

# ===== BASIC ROUTES =====

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
    
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=session['username'], user=user)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/feed')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('feed.html', posts=posts)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        
        if not content:
            return render_template('create_post.html', error='Post content cannot be empty')
        
        new_post = Post(content=content, user_id=session['user_id'])
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('feed'))
    
    return render_template('create_post.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ===== SIMPLE CHAT ROUTES =====

@app.route('/messages')
def messages():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get user's chats
    chats1 = Chat.query.filter_by(user1_id=user.id).all()
    chats2 = Chat.query.filter_by(user2_id=user.id).all()
    all_chats = chats1 + chats2
    
    return render_template('messages_simple.html', user=user, chats=all_chats)

@app.route('/chat/<int:user_id>')
def start_chat(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    target_user = User.query.get(user_id)
    if not target_user:
        return redirect(url_for('messages'))
    
    # Find existing chat
    chat = Chat.query.filter(
        ((Chat.user1_id == session['user_id']) & (Chat.user2_id == user_id)) |
        ((Chat.user1_id == user_id) & (Chat.user2_id == session['user_id']))
    ).first()
    
    if not chat:
        # Create new chat
        chat = Chat(user1_id=session['user_id'], user2_id=user_id)
        db.session.add(chat)
        db.session.commit()
    
    messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.created_at.asc()).all()
    
    return render_template('chat_simple.html', chat=chat, target_user=target_user, user=User.query.get(session['user_id']), messages=messages)

# ===== WEB SOCKET HANDLERS =====

@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        join_room(f"user_{session['user_id']}")
        print(f"✅ User {session['user_id']} connected to chat")
        emit('connection_status', {'status': 'connected', 'user_id': session['user_id']})

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        leave_room(f"user_{session['user_id']}")
        print(f"❌ User {session['user_id']} disconnected")

@socketio.on('join_chat')
def handle_join_chat(data):
    chat_id = data['chat_id']
    join_room(f"chat_{chat_id}")
    print(f"💬 User {session['user_id']} joined chat {chat_id}")

@socketio.on('send_message')
def handle_send_message(data):
    if 'user_id' not in session:
        return {'success': False, 'error': 'Not authenticated'}
    
    chat_id = data['chat_id']
    content = data['content'].strip()
    
    if not content:
        return {'success': False, 'error': 'Message cannot be empty'}
    
    # Verify user is part of this chat
    chat = Chat.query.get(chat_id)
    if not chat or (chat.user1_id != session['user_id'] and chat.user2_id != session['user_id']):
        return {'success': False, 'error': 'Not authorized for this chat'}
    
    # Create and save message
    new_message = Message(
        content=content,
        chat_id=chat_id,
        sender_id=session['user_id']
    )
    
    # Update chat's last message time
    chat.last_message_at = datetime.utcnow()
    
    db.session.add(new_message)
    db.session.commit()
    
    # Prepare response
    message_data = {
        'id': new_message.id,
        'content': new_message.content,
        'sender_id': new_message.sender_id,
        'sender_username': User.query.get(new_message.sender_id).username,
        'created_at': new_message.created_at.isoformat(),
        'chat_id': chat_id
    }
    
    # Send to all participants in the chat room
    emit('new_message', message_data, room=f"chat_{chat_id}")
    
    return {'success': True, 'message': message_data}

@socketio.on('typing_start')
def handle_typing_start(data):
    chat_id = data['chat_id']
    emit('user_typing', {
        'user_id': session['user_id'],
        'username': User.query.get(session['user_id']).username,
        'typing': True
    }, room=f"chat_{chat_id}", include_self=False)

@socketio.on('typing_stop')
def handle_typing_stop(data):
    chat_id = data['chat_id']
    emit('user_typing', {
        'user_id': session['user_id'],
        'username': User.query.get(session['user_id']).username,
        'typing': False
    }, room=f"chat_{chat_id}", include_self=False)

# ===== INITIALIZE DATABASE =====

def init_db():
    with app.app_context():
        print("🔄 Creating clean database...")
        db.drop_all()
        db.create_all()
        
        # Create test users
        test_user = User(username='test', email='test@nexus.com')
        test_user.set_password('test123')
        test_user.full_name = "Test User"
        test_user.bio = "Welcome to Nexus!"
        db.session.add(test_user)
        
        alice = User(username='alice', email='alice@nexus.com')
        alice.set_password('alice123')
        alice.full_name = "Alice Wonderland"
        alice.bio = "Exploring digital worlds"
        db.session.add(alice)
        
        bob = User(username='bob', email='bob@nexus.com')
        bob.set_password('bob123')
        bob.full_name = "Bob Builder"
        bob.bio = "Building amazing things"
        db.session.add(bob)
        
        # Create sample posts
        posts = [
            "Welcome to Nexus! 🚀 This platform is getting chat features!",
            "Real-time messaging coming soon... 💬",
            "Building the future of social communication! ⚡"
        ]
        
        for i, content in enumerate(posts):
            post = Post(content=content, user_id=1)
            db.session.add(post)
        
        db.session.commit()
        print("✅ Clean database created successfully!")
        print("🔑 test/test123 | alice/alice123 | bob/bob123")

if __name__ == '__main__':
    init_db()
    print("🚀 NEXUS CLEAN VERSION STARTING...")
    print("📍 http://localhost:5000")
    print("🌐 Check your phone's IP address")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
