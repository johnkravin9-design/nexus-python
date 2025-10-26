from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from PIL import Image
from werkzeug.utils import secure_filename

# === DECORATORS MUST BE DEFINED FIRST ===
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        # You'll need to add 'role' field to User model later
        if not user or not hasattr(user, 'role') or user.role != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function
# === END DECORATORS ===

try:
    from video_utils import save_video_file, VideoProcessor, save_video_file_fallback
    VIDEO_SUPPORT = True
except ImportError:
    VIDEO_SUPPORT = False
    print("Video support disabled - required dependencies not installed")

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

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    profile_picture = db.Column(db.String(200))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Add this for admin functionality:
    role = db.Column(db.String(20), default='user')

# ... rest of your existing code continues exactly as before ...
