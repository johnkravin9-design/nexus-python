from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Drop and recreate tables to add new columns (WARNING: This will delete all data!)
    print("⚠️  This will reset your database and delete all existing data!")
    response = input("Continue? (y/n): ")
    
    if response.lower() == 'y':
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            email='admin@nexus.com',
            is_admin=True
        )
        db.session.add(admin)
        
        # Create a regular test user
        test_user = User(
            username='test',
            password=generate_password_hash('test123'),
            email='test@nexus.com',
            is_admin=False
        )
        db.session.add(test_user)
        
        db.session.commit()
        print("✅ Database reset and admin user created!")
        print("👑 Admin: username='admin', password='admin123'")
        print("👤 Test: username='test', password='test123'")
    else:
        print("❌ Cancelled. No changes made.")
