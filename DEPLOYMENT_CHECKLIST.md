# Render Deployment Checklist

## ✅ Pre-Deployment
- [ ] Pillow added to requirements.txt
- [ ] All SQLAlchemy deprecations fixed
- [ ] All datetime.utcnow() replaced
- [ ] PORT environment variable support added
- [ ] gunicorn in requirements.txt
- [ ] Database configuration for production

## 🔧 Render Configuration
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`

## 🌐 Environment Variables
- `SECRET_KEY`: Generate a secure random key
- `DATABASE_URL`: Provided by Render PostgreSQL
- `PORT`: Automatically set by Render

## 🚀 Deployment Steps
1. Push all changes to GitHub
2. Connect repository to Render
3. Set environment variables
4. Deploy
