# Add this to your app.py in the models section
from datetime import datetime

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reported_post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    reported_comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref=db.backref('reports_made', lazy=True))
    reported_user = db.relationship('User', foreign_keys=[reported_user_id], backref=db.backref('reports_against', lazy=True))
    reported_post = db.relationship('Post', backref=db.backref('reports', lazy=True))
    reported_comment = db.relationship('Comment', backref=db.backref('reports', lazy=True))
