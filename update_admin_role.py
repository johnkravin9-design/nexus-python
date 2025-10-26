from app import app, db, User
import sqlite3

def add_admin_role():
    with app.app_context():
        try:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if role column exists
            cursor.execute("PRAGMA table_info(user)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'role' not in columns:
                print("➕ Adding role column to user table...")
                cursor.execute('ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT "user"')
            
            conn.commit()
            conn.close()
            print("✅ Database updated for admin role!")
            
            # Create admin user if doesn't exist
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                from werkzeug.security import generate_password_hash
                admin_user = User(
                    username='admin',
                    email='admin@nexus.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Created admin user: admin / admin123")
            else:
                # Update existing admin user
                admin_user.role = 'admin'
                db.session.commit()
                print("✅ Updated existing admin user with admin role")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    add_admin_role()
