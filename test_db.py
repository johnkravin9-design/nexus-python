from app import app, db, User

with app.app_context():
    # Drop all tables and recreate
    db.drop_all()
    db.create_all()
    
    # Test if the role column exists
    try:
        # Create a test user
        test_user = User(username='test', email='test@test.com', password_hash='test')
        db.session.add(test_user)
        db.session.commit()
        print("✓ Database created successfully with role column")
        
        # Query to verify role exists
        user = User.query.filter_by(username='test').first()
        if hasattr(user, 'role'):
            print(f"✓ Role column exists: {user.role}")
        else:
            print("✗ Role column missing")
            
    except Exception as e:
        print(f"✗ Error: {e}")
