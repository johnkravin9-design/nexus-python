# Add to your app.py models section

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # like, comment, message, system
    related_id = db.Column(db.Integer, nullable=True)  # post_id, comment_id, etc
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

# Notification functions
def create_notification(user_id, title, message, notif_type, related_id=None):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notif_type,
        related_id=related_id
    )
    db.session.add(notification)
    db.session.commit()
    
    # Emit real-time notification via SocketIO
    socketio.emit('new_notification', {
        'title': title,
        'message': message,
        'type': notif_type,
        'id': notification.id
    }, room=f'user_{user_id}')
    
    return notification

# Add these routes
@app.route('/notifications')
def notifications_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_notifications = Notification.query.filter_by(
        user_id=session['user_id']
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('notifications.html', notifications=user_notifications)

@app.route('/notifications/read/<int:notif_id>', methods=['POST'])
def mark_notification_read(notif_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    notification = Notification.query.filter_by(
        id=notif_id, 
        user_id=session['user_id']
    ).first()
    
    if notification:
        notification.is_read = True
        db.session.commit()
    
    return jsonify({'success': True})

@app.route('/notifications/count')
def notification_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    
    count = Notification.query.filter_by(
        user_id=session['user_id'],
        is_read=False
    ).count()
    
    return jsonify({'count': count})

# SocketIO events for real-time notifications
@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        user_id = session['user_id']
        join_room(f'user_{user_id}')
        print(f'User {user_id} connected for notifications')

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        user_id = session['user_id']
        leave_room(f'user_{user_id}')
        print(f'User {user_id} disconnected')
