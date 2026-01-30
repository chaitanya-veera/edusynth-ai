@echo off
echo Starting EduSynth AI Application...
echo.

echo Checking database setup...
python setup_db.py

echo.
echo Starting Flask application...
echo Open your browser and go to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py