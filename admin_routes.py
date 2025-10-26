from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = db.session.get(User, session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_posts': Post.query.count(), 
        'total_reports': Report.query.count(),
        'pending_reports': Report.query.filter_by(status='pending').count()
    }
    
    recent_reports = Report.query.filter_by(status='pending').order_by(Report.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', stats=stats, recent_reports=recent_reports, recent_users=recent_users)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)

@app.route('/report', methods=['POST'])
def report_content():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    reporter_id = session['user_id']
    reported_user_id = request.form.get('reported_user_id')
    reported_post_id = request.form.get('reported_post_id') 
    reported_comment_id = request.form.get('reported_comment_id')
    reason = request.form.get('reason')
    
    if not reason:
        return jsonify({'error': 'Reason is required'}), 400
    
    report = Report(
        reporter_id=reporter_id,
        reported_user_id=reported_user_id,
        reported_post_id=reported_post_id,
        reported_comment_id=reported_comment_id,
        reason=reason
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Report submitted successfully'})

@app.route('/admin/ban/<int:user_id>', methods=['POST'])
@admin_required
def ban_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        user.is_banned = True
        db.session.commit()
        flash(f'User {user.username} has been banned', 'error')
    return redirect(url_for('admin_users'))

@app.route('/admin/unban/<int:user_id>', methods=['POST'])
@admin_required
def unban_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        user.is_banned = False
        db.session.commit()
        flash(f'User {user.username} has been unbanned', 'success')
    return redirect(url_for('admin_users'))
