from app import app, db, User, Post

def setup_test_data():
    with app.app_context():
        try:
            # Create test users if they don't exist
            users_data = [
                {'username': 'alice', 'email': 'alice@example.com', 'password_hash': 'test123'},
                {'username': 'bob', 'email': 'bob@example.com', 'password_hash': 'test123'},
                {'username': 'charlie', 'email': 'charlie@example.com', 'password_hash': 'test123'}
            ]
            
            for user_data in users_data:
                if not User.query.filter_by(username=user_data['username']).first():
                    user = User(**user_data)
                    db.session.add(user)
                    print(f"✅ Created user: {user_data['username']}")
            
            db.session.commit()
            
            # Create test posts
            users = User.query.all()
            sample_posts = [
                "Just launched my new project! 🚀 So excited to share it with the world! #coding #webdev",
                "Beautiful sunset today! Nature always knows how to inspire. 🌅",
                "Working on some exciting new features for our platform. Stay tuned! 👨‍💻",
                "Just finished reading an amazing book about AI and the future. Mind = blown! 🤯",
                "Coffee + coding = perfect morning ☕️ What's everyone working on today?",
                "Exploring new hiking trails this weekend! Any recommendations? 🏞️"
            ]
            
            for i, post_content in enumerate(sample_posts):
                if i < len(users):
                    post = Post(
                        content=post_content,
                        user_id=users[i].id
                    )
                    db.session.add(post)
                    print(f"✅ Created post: {post_content[:50]}...")
            
            db.session.commit()
            print("🎉 Test data setup completed successfully!")
            
            # Verify everything works
            posts = Post.query.join(User).all()
            for post in posts:
                print(f"Post by {post.user.username}: {post.content[:50]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    setup_test_data()
