from app import app, db, User, Post, Message, Chat, ChatParticipant

def fix_relationships():
    with app.app_context():
        try:
            # Test the relationships
            user = User.query.first()
            if user:
                print(f"User: {user.username}")
                
                # Create a test post if none exist
                if not Post.query.first():
                    test_post = Post(
                        content="Welcome to Nexus! This is a test post.",
                        user_id=user.id
                    )
                    db.session.add(test_post)
                    db.session.commit()
                    print("✅ Created test post")
                
                # Test the relationship
                posts = Post.query.all()
                for post in posts:
                    print(f"Post: {post.content}")
                    print(f"Post user: {post.user.username if post.user else 'No user'}")
                    
            else:
                print("❌ No users found. Please create a user first.")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    fix_relationships()
