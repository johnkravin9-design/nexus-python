from app import app, db, Message
import sqlite3
import os

def migrate_messages():
    with app.app_context():
        try:
            print("Starting database migration...")
            
            # Get database path
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            print(f"Database path: {db_path}")
            
            if not os.path.exists(db_path):
                print("❌ Database file not found!")
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check existing columns
            cursor.execute("PRAGMA table_info(message)")
            existing_columns = [column[1] for column in cursor.fetchall()]
            print(f"Existing columns: {existing_columns}")
            
            # Columns to add
            columns_to_add = [
                ('is_read', 'BOOLEAN DEFAULT 0'),  # SQLite uses 0/1 for boolean
                ('message_type', 'TEXT DEFAULT "text"'),
                ('file_path', 'TEXT'),
                ('filename', 'TEXT'),
                ('file_size', 'INTEGER')
            ]
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    print(f"➕ Adding column: {column_name}")
                    try:
                        cursor.execute(f'ALTER TABLE message ADD COLUMN {column_name} {column_type}')
                        print(f"✅ Successfully added {column_name}")
                    except Exception as e:
                        print(f"❌ Failed to add {column_name}: {e}")
                else:
                    print(f"✅ Column {column_name} already exists")
            
            conn.commit()
            conn.close()
            print("🎉 Database migration completed successfully!")
            
        except Exception as e:
            print(f"💥 Migration failed: {e}")

if __name__ == '__main__':
    migrate_messages()
