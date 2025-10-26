from app import app, db
import sqlite3
import os

def fix_message_table():
    with app.app_context():
        try:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check current message table columns
            cursor.execute("PRAGMA table_info(message)")
            columns = [col[1] for col in cursor.fetchall()]
            print("Current message columns:", columns)
            
            # Add missing columns
            missing_columns = ['is_read', 'message_type', 'file_path', 'filename', 'file_size']
            
            for column in missing_columns:
                if column not in columns:
                    print(f"Adding column: {column}")
                    if column == 'is_read':
                        cursor.execute(f'ALTER TABLE message ADD COLUMN {column} BOOLEAN DEFAULT 0')
                    elif column in ['message_type', 'file_path', 'filename']:
                        cursor.execute(f'ALTER TABLE message ADD COLUMN {column} VARCHAR(255)')
                    elif column == 'file_size':
                        cursor.execute(f'ALTER TABLE message ADD COLUMN {column} INTEGER')
            
            conn.commit()
            conn.close()
            print("✅ Message table updated successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    fix_message_table()
