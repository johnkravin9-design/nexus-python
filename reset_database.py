from app import app, db
import os

def reset_database():
    with app.app_context():
        try:
            # Remove the existing database file
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if os.path.exists(db_path):
                os.remove(db_path)
                print("🗑️ Removed old database file")
            
            # Create all tables with current models
            db.create_all()
            print("✅ All tables created successfully with current schema!")
            
            # Verify tables and columns
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Created tables: {tables}")
            
            # Check Post table columns
            if 'post' in tables:
                columns = inspector.get_columns('post')
                print("📝 Post table columns:")
                for col in columns:
                    print(f"   ✅ {col['name']}: {col['type']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    reset_database()
