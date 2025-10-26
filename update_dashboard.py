import re

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Update the dashboard route to use join for posts
old_dashboard = """@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('dashboard.html', user=user, posts=posts)"""

new_dashboard = """@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    posts = Post.query.join(User).order_by(Post.created_at.desc()).all()
    return render_template('dashboard.html', user=user, posts=posts)"""

# Replace the dashboard route
content = content.replace(old_dashboard, new_dashboard)

# Also update the feed route
old_feed = """@app.route('/feed')
@login_required
def feed():
    user = User.query.get(session['user_id'])
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('feed.html', user=user, posts=posts)"""

new_feed = """@app.route('/feed')
@login_required
def feed():
    user = User.query.get(session['user_id'])
    posts = Post.query.join(User).order_by(Post.created_at.desc()).all()
    return render_template('feed.html', user=user, posts=posts)"""

content = content.replace(old_feed, new_feed)

# Write the updated content back
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Updated dashboard and feed routes to use proper relationship loading")
