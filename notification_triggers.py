# Add these to your existing routes

# In like route, after successful like:
def like_post(post_id):
    # ... existing like logic ...
    
    # Create notification for post owner
    post = db.session.get(Post, post_id)
    if post.user_id != session['user_id']:  # Don't notify yourself
        create_notification(
            user_id=post.user_id,
            title="New Like",
            message=f"{current_user.username} liked your post",
            notif_type="like",
            related_id=post_id
        )
    
    return jsonify({'success': True})

# In comment route, after successful comment:
def comment_post(post_id):
    # ... existing comment logic ...
    
    # Create notification for post owner
    post = db.session.get(Post, post_id)
    if post.user_id != session['user_id']:  # Don't notify yourself
        create_notification(
            user_id=post.user_id,
            title="New Comment",
            message=f"{current_user.username} commented on your post",
            notif_type="comment",
            related_id=post_id
        )
    
    return jsonify({'success': True})

# In message route:
def send_message():
    # ... existing message logic ...
    
    # Create notification for receiver
    create_notification(
        user_id=receiver_id,
        title="New Message",
        message=f"{current_user.username} sent you a message",
        notif_type="message"
    )
    
    return jsonify({'success': True})
