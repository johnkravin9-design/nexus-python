from app import app, db, User
from werkzeug.security import generate_password_hash
import sqlite3
import os

def migrate_with_data():
    with app.app_context():
        # Backup current data
        print("Backing up current data...")
        
        # Get all current users
        current_users = User.query.all()
        print(f"Found {len(current_users)} users to migrate")
        
        # Create temporary backup
        user_backup = []
        for user in current_users:
            user_backup.append({
                'username': user.username,
                'password': user.password,
                'created_at': user.created_at
            })
        
        # Drop and recreate tables
        db.drop_all()
        db.create_all()
        
        # Restore users with new fields
        for user_data in user_backup:
            user = User(
                username=user_data['username'],
                password=user_data['password'],
                created_at=user_data['created_at'],
                is_admin=False,
                is_banned=False,
                warnings=0
            )
            # Make first user admin
            if user_data['username'] == 'admin':
                user.is_admin = True
            db.session.add(user)
        
        # Create admin if it doesn't exist
        if not any(user['username'] == 'admin' for user in user_backup):
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@nexus.com',
                is_admin=True
            )
            db.session.add(admin)
            print("✅ Created new admin user")
        
        db.session.commit()
        print("✅ Migration completed successfully!")
        print("👑 Admin: username='admin', password='admin123'")

migrate_with_data()
