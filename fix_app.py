# Fix for SQLAlchemy warnings and like/comment functionality

# Replace these specific lines in your app.py:

# Line ~371: Change from:
user = User.query.get(session['user_id'])
# To:
user = db.session.get(User, session['user_id'])

# Line ~378: Change from:
user = User.query.get(session['user_id'])
# To:
user = db.session.get(User, session['user_id'])

# Line ~734: Change from:
comment_with_user = Comment.query.options(db.joinedload(Comment.user)).get(new_comment.id)
# To:
comment_with_user = db.session.get(Comment, new_comment.id)

# Update like route to return JSON:
@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    user = db.session.get(User, user_id)
    
    existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    post = db.session.get(Post, post_id)
    
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        new_like = Like(user_id=user_id, post_id=post_id)
        db.session.add(new_like)
        liked = True
    
    db.session.commit()
    
    like_count = Like.query.filter_by(post_id=post_id).count()
    
    return jsonify({
        'liked': liked,
        'like_count': like_count,
        'post_id': post_id
    })

# Update comment route to return JSON:
@app.route('/comment/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    content = request.form.get('content')
    
    if not content:
        return jsonify({'error': 'Comment content required'}), 400
    
    new_comment = Comment(
        content=content,
        user_id=user_id,
        post_id=post_id
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    comment_with_user = db.session.get(Comment, new_comment.id)
    
    return jsonify({
        'success': True,
        'comment': {
            'id': comment_with_user.id,
            'content': comment_with_user.content,
            'created_at': comment_with_user.created_at.strftime('%Y-%m-%d %H:%M'),
            'user': {
                'username': comment_with_user.user.username
            }
        }
    })
