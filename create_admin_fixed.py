from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    print("Creating admin user with correct field names...")
    
    # Check if admin already exists
    existing_admin = User.query.filter_by(username='admin').first()
    if existing_admin:
        print("Admin user already exists, updating...")
        existing_admin.password_hash = generate_password_hash('admin123')
        existing_admin.email = 'admin@nexus.com'
        existing_admin.role = 'admin'  # Use the role field instead of is_admin
        db.session.commit()
        print("✅ Admin user updated!")
    else:
        # Create new admin user
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            email='admin@nexus.com',
            role='admin'  # Using the 'role' field that exists in your model
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created successfully!")
    
    print("👑 Admin credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   Email: admin@nexus.com")
    print("   Role: admin")
