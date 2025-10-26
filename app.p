from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexus-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nexus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model with ALL profile fields
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Profile fields
    full_name = db.Column(db.String(100), default='')
    bio = db.Column(db.Text, default='')
    location = db.Column(db.String(100), default='')
    website = db.Column(db.String(200), default='')
    profile_picture = db.Column(db.String(200), default='default_avatar.png')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Connection Model for Follow System
class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    follower = db.relationship('User', foreign_keys=[follower_id], backref='following')
    following = db.relationship('User', foreign_keys=[following_id], backref='followers')

# Routes
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Profile Routes
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
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
    
    is_following = Connection.query.filter_by(
        follower_id=session['user_id'], 
        following_id=user.id
    ).first() is not None
    
    return render_template('public_profile.html', 
                         user=user, 
                         is_own_profile=is_own_profile,
                         is_following=is_following)

@app.route('/follow/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    if session['user_id'] == user_id:
        return jsonify({'success': False, 'message': 'Cannot follow yourself'})
    
    existing_connection = Connection.query.filter_by(
        follower_id=session['user_id'],
        following_id=user_id
    ).first()
    
    if not existing_connection:
        new_connection = Connection(
            follower_id=session['user_id'],
            following_id=user_id
        )
        db.session.add(new_connection)
        db.session.commit()
    
    return jsonify({'success': True, 'message': 'Followed successfully'})

@app.route('/unfollow/<int:user_id>', methods=['POST'])
def unfollow_user(user_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    connection = Connection.query.filter_by(
        follower_id=session['user_id'],
        following_id=user_id
    ).first()
    
    if connection:
        db.session.delete(connection)
        db.session.commit()
    
    return jsonify({'success': True, 'message': 'Unfollowed successfully'})

# Initialize database - THIS WILL RESET THE DATABASE
def init_db():
    with app.app_context():
        # Drop all tables and recreate with new schema
        db.drop_all()
        db.create_all()
        
        # Create test user
        test_user = User(username='test', email='test@nexus.com')
        test_user.set_password('test123')
        db.session.add(test_user)
        db.session.commit()
        print("✅ Database reset and test user created: test / test123")

if __name__ == '__main__':
    init_db()
    print("🚀 Nexus app starting on http://localhost:5000")
    print("🔑 Test credentials: test / test123")
    print("📱 Access from network: http://10.81.93.48:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
