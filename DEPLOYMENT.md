# 🚀 EduSynth AI - Render Deployment Guide

## Prerequisites
1. GitHub account with your code pushed
2. Render account (free tier available)
3. MySQL database (use PlanetScale or Render PostgreSQL)

## Step 1: Prepare Database

### Option A: PlanetScale (Recommended)
1. Go to https://planetscale.com
2. Create free account
3. Create new database: "edusynth-ai"
4. Get connection string
5. Run setup script to create tables

### Option B: Render PostgreSQL
1. Create PostgreSQL database on Render
2. Modify db.py to use PostgreSQL instead of MySQL

## Step 2: Deploy on Render

### 2.1 Create Web Service
1. Go to https://render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - Name: edusynth-ai
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: python app.py

### 2.2 Set Environment Variables
Add these in Render dashboard:

```
GEMINI_API_KEY=your_gemini_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
DATABASE_URL=mysql://user:pass@host:port/database
SMTP_EMAIL=your_gmail_address
SMTP_PASSWORD=your_gmail_app_password
```

### 2.3 Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Wait for deployment to complete
4. Access your app at: https://your-app-name.onrender.com

## Step 3: Database Setup

### Run this after deployment:
```python
# Create tables in production database
python setup_db.py
```

## Step 4: Test Deployment

1. Visit your Render URL
2. Test user registration
3. Test all features:
   - PDF analysis
   - YouTube analysis
   - Web content analysis
   - Quiz generation

## Environment Variables Needed:

```env
# Required
GEMINI_API_KEY=AIzaSyA-yuE_ZDlzHfcRXSNMON5PKLN5ZVp3WVI
DATABASE_URL=mysql://user:password@host:port/database

# Optional
YOUTUBE_API_KEY=your_youtube_api_key
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## Troubleshooting:

### Build Fails:
- Check requirements.txt has all dependencies
- Ensure Python version compatibility

### Database Connection Error:
- Verify DATABASE_URL format
- Check database is accessible from Render

### App Crashes:
- Check Render logs
- Ensure all environment variables are set
- Verify port configuration (app runs on PORT env var)

## Free Tier Limitations:
- App sleeps after 15 minutes of inactivity
- 750 hours/month free
- Slower cold starts

## Production Checklist:
- ✅ Environment variables set
- ✅ Database connected
- ✅ Tables created
- ✅ API keys working
- ✅ All features tested
- ✅ SSL enabled (automatic on Render)

Your app will be live at: https://your-app-name.onrender.com