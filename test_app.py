from app import app, db, User, Post

def test_app():
    with app.app_context():
        # Create a test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash='test_hash'  # In real app, use generate_password_hash
        )
        db.session.add(test_user)
        db.session.commit()
        
        # Create a test post
        test_post = Post(
            content='This is a test post!',
            user_id=test_user.id
        )
        db.session.add(test_post)
        db.session.commit()
        
        # Verify data
        users = User.query.all()
        posts = Post.query.all()
        
        print(f"✅ Users in database: {len(users)}")
        print(f"✅ Posts in database: {len(posts)}")
        
        for user in users:
            print(f"   👤 {user.username} ({user.email})")
        
        for post in posts:
            print(f"   📝 Post by {post.user.username}: {post.content}")

if __name__ == '__main__':
    test_app()
