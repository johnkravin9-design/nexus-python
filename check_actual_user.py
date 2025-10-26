from app import app, User

with app.app_context():
    # Check what fields your User model actually has
    print("User model attributes:")
    for attr in dir(User):
        if not attr.startswith('_'):
            print(f"  {attr}")
    
    # Check table columns
    print("\nTable columns:")
    for column in User.__table__.columns:
        print(f"  {column.name} ({column.type})")
    
    # Try to see what happens when we create a user
    try:
        test = User(username='test')
        print("\n✅ User can be created with username")
    except Exception as e:
        print(f"\n❌ Error creating user: {e}")
