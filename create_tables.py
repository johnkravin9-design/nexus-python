from app import app, db
import os

def create_all_tables():
    with app.app_context():
        try:
            # Drop and recreate all tables to ensure they exist
            db.drop_all()
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables created: {tables}")
            
            # Check message table specifically
            if 'message' in tables:
                columns = [col['name'] for col in inspector.get_columns('message')]
                print(f"📝 Message table columns: {columns}")
            else:
                print("❌ Message table was not created!")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    create_all_tables()
