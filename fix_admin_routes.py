# Add this to your app.py or replace existing admin_required decorator

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = db.session.get(User, session['user_id'])
        if not user or user.role != 'admin':  # Check role instead of is_admin
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Example admin route
@app.route('/admin')
@admin_required
def admin_dashboard():
    # Your admin dashboard code here
    total_users = User.query.count()
    return f"Admin Dashboard - Total Users: {total_users}"
