from app import app, db, Post, Message
import sqlite3
import os

def update_models_for_video():
    with app.app_context():
        try:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Add video columns to Post table
            cursor.execute("PRAGMA table_info(post)")
            post_columns = [col[1] for col in cursor.fetchall()]
            
            video_columns = ['video_url', 'video_thumbnail', 'video_duration', 'media_type']
            
            for column in video_columns:
                if column not in post_columns:
                    print(f"➕ Adding {column} to post table...")
                    if column == 'video_duration':
                        cursor.execute(f'ALTER TABLE post ADD COLUMN {column} INTEGER')
                    else:
                        cursor.execute(f'ALTER TABLE post ADD COLUMN {column} VARCHAR(255)')
            
            # Add video support to Message table
            cursor.execute("PRAGMA table_info(message)")
            message_columns = [col[1] for col in cursor.fetchall()]
            
            if 'video_url' not in message_columns:
                print("➕ Adding video_url to message table...")
                cursor.execute('ALTER TABLE message ADD COLUMN video_url VARCHAR(255)')
            
            conn.commit()
            conn.close()
            print("✅ Database updated for video support!")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    update_models_for_video()
