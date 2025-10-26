from app import app, db
import sqlite3
import os

def fix_post_model():
    with app.app_context():
        try:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            # Check current Post table structure
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(post)")
            columns = cursor.fetchall()
            print("Current Post table columns:")
            for col in columns:
                print(f"   {col[1]} ({col[2]})")
            
            conn.close()
            
            # The table shows image_url but code expects image_path
            # We have two options:
            print("\n🔧 OPTIONS:")
            print("1. Rename image_url to image_path in database")
            print("2. Update app.py to use image_url instead of image_path")
            print("\nLet's check what the app.py expects...")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    fix_post_model()
