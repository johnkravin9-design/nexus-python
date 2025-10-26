from app import app, db
import sqlite3
import os

def migrate_database():
    with app.app_context():
        try:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            if not os.path.exists(db_path):
                print("Creating new database...")
                db.create_all()
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if post table has image_path column
            cursor.execute("PRAGMA table_info(post)")
            post_columns = [column[1] for column in cursor.fetchall()]
            print(f"Post table columns: {post_columns}")
            
            # Add missing columns
            if 'image_path' not in post_columns:
                print("➕ Adding image_path to post table...")
                cursor.execute('ALTER TABLE post ADD COLUMN image_path VARCHAR(200)')
            
            # Check other tables for missing columns
            tables_to_check = {
                'message': ['is_read', 'message_type', 'file_path', 'filename', 'file_size'],
                'chat': ['last_message_at']
            }
            
            for table, columns in tables_to_check.items():
                cursor.execute(f"PRAGMA table_info({table})")
                existing_columns = [col[1] for col in cursor.fetchall()]
                
                for column in columns:
                    if column not in existing_columns:
                        print(f"➕ Adding {column} to {table} table...")
                        if column == 'is_read':
                            cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} BOOLEAN DEFAULT 0')
                        elif column in ['message_type', 'file_path', 'filename']:
                            cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} VARCHAR(255)')
                        elif column == 'file_size':
                            cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} INTEGER')
                        elif column == 'last_message_at':
                            cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} DATETIME')
                        elif column == 'image_path':
                            cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} VARCHAR(200)')
            
            conn.commit()
            conn.close()
            print("✅ Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")

if __name__ == '__main__':
    migrate_database()
