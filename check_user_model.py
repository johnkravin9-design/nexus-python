from app import app, db, User

with app.app_context():
    # Check if User model has is_admin field
    user_columns = [column.name for column in User.__table__.columns]
    print("User model columns:", user_columns)
    
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"Admin user found: {admin.username}")
        print(f"Is admin: {getattr(admin, 'is_admin', 'NO is_admin FIELD')}")
    else:
        print("No admin user found")
