def init_db():
    """Initialize the database with sample data"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_sample_data()
        print("🔄 Creating fresh master database...")
