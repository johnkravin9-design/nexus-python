from app import app, User
from werkzeug.security import check_password_hash

with app.app_context():
    # Test login credentials
    username = 'admin'
    password = 'admin123'
    
    user = User.query.filter_by(username=username).first()
    
    if user:
        print(f"✅ User found: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🎯 Role: {user.role}")
        print(f"🔑 Password hash: {user.password_hash[:30]}...")
        
        # Test password verification
        if check_password_hash(user.password_hash, password):
            print("✅ Password verification: SUCCESS")
            print("🎉 You can now login as admin!")
            
            if user.role == 'admin':
                print("⚡ ADMIN PRIVILEGES CONFIRMED!")
                print("🌐 Login at: http://localhost:5000/login")
                print("   Then visit: http://localhost:5000/admin")
            else:
                print("⚠️  User exists but is not an admin")
        else:
            print("❌ Password verification: FAILED")
    else:
        print("❌ User not found")
