from app import app, db

def init_database():
    with app.app_context():
        try:
            print("Creating all database tables...")
            
            # Create all tables that exist in your models
            db.create_all()
            
            print("✅ All tables created successfully!")
            
            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Existing tables: {tables}")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")

if __name__ == '__main__':
    init_database()
