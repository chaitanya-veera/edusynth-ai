# Production Environment Variables for Render/Vercel

Set these environment variables in your deployment platform:

## Required Variables:
GEMINI_API_KEY=AIzaSyBu0QSENsa8IfFygptHQCLeTk1SqsDkOd0
YOUTUBE_API_KEY=AIzaSyBrZwCIMPJ_penJqsKUfxO76dLUnQotafQ

## Database (Use your production database URL):
DATABASE_URL=mysql://username:password@host:port/database_name

## OR individual database variables:
DB_HOST=your_production_host
DB_USER=your_production_user  
DB_PASSWORD=your_production_password
DB_NAME=your_production_database

## Email (Optional):
SMTP_EMAIL=your.email@gmail.com
SMTP_PASSWORD=your_app_password

## Steps to fix:
1. Go to your Render/Vercel dashboard
2. Find your deployed app
3. Go to Environment Variables section
4. Add the above variables
5. Redeploy the application