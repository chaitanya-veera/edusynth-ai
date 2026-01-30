from flask import Flask, request, jsonify, render_template, session, redirect, flash, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import smtplib, ssl, random, os, re, time, json, requests, bcrypt
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from gemini_fallback import gemini_response
from db import get_connection
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime, timedelta
import mysql.connector

# Initialize
load_dotenv()
app = Flask(__name__)
app.secret_key = "secret123"

# Environment variables
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Create tables
def create_tables():
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                mobile VARCHAR(20),
                college VARCHAR(255),
                branch VARCHAR(255),
                year VARCHAR(50),
                language VARCHAR(50),
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create user_activity table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                activity_type VARCHAR(50) NOT NULL,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Table creation error: {e}")

create_tables()

# Routes
@app.route("/")
def landing():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signuppage")
def signuppage():
    return render_template("signup.html")

@app.route("/logout")
def logout():
    if "user_id" in session:
        try:
            # Clear user's activity history from database
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM user_activity WHERE user_id = %s", (session["user_id"],))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error clearing history: {e}")
    
    session.clear()
    return redirect("/")

@app.route("/forget")
def forget():
    return render_template("forget.html")

@app.route("/forgot", methods=["POST"])
def forgot():
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower() if data else ""
        
        if not email:
            return jsonify({"success": False, "message": "Email is required"})
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"success": False, "message": "Email not found in our records"})
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        session["reset_otp"] = otp
        session["reset_email"] = email
        session["otp_time"] = time.time()
        
        # For now, just print OTP (you can implement email sending later)
        print(f"Password Reset OTP for {email}: {otp}")
        
        return jsonify({
            "success": True, 
            "message": f"OTP sent to {email}. Check console for OTP (Demo mode)"
        })
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        return jsonify({"success": False, "message": "Failed to process request"})

@app.route("/verify", methods=["POST"])
def verify():
    try:
        data = request.get_json()
        otp = data.get("otp", "").strip() if data else ""
        
        if not otp:
            return jsonify({"success": False, "message": "OTP is required"})
        
        if "reset_otp" not in session:
            return jsonify({"success": False, "message": "No OTP session found. Please request a new OTP."})
        
        # Check OTP expiry (10 minutes)
        if time.time() - session.get("otp_time", 0) > 600:
            session.pop("reset_otp", None)
            session.pop("reset_email", None)
            session.pop("otp_time", None)
            return jsonify({"success": False, "message": "OTP expired. Please request a new one."})
        
        if otp != session["reset_otp"]:
            return jsonify({"success": False, "message": "Invalid OTP. Please try again."})
        
        session["otp_verified"] = True
        return jsonify({"success": True, "message": "OTP verified successfully. You can now reset your password."})
        
    except Exception as e:
        print(f"OTP verification error: {e}")
        return jsonify({"success": False, "message": "Verification failed. Please try again."})

@app.route("/reset-password", methods=["POST"])
def reset_password():
    try:
        data = request.get_json()
        password = data.get("password", "").strip() if data else ""
        
        if not password:
            return jsonify({"success": False, "message": "Password is required"})
        
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters long"})
        
        if not session.get("otp_verified"):
            return jsonify({"success": False, "message": "OTP not verified. Please verify OTP first."})
        
        email = session.get("reset_email")
        if not email:
            return jsonify({"success": False, "message": "Session expired. Please start over."})
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Hash new password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password
        cur.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_password, email))
        conn.commit()
        conn.close()
        
        # Clear all session data
        session.pop("reset_otp", None)
        session.pop("reset_email", None)
        session.pop("otp_verified", None)
        session.pop("otp_time", None)
        
        return jsonify({"success": True, "message": "Password updated successfully. You can now login with your new password."})
        
    except Exception as e:
        print(f"Password reset error: {e}")
        return jsonify({"success": False, "message": "Failed to update password. Please try again."})

@app.route("/logingo", methods=["POST"])
def logingo():
    try:
        email = request.form.get("user_email", "").strip().lower()
        password = request.form.get("user_pass", "")

        if not email or not password:
            flash("Email and password are required")
            return redirect("/login")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, full_name, password FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        conn.close()

        if not user:
            flash("Invalid email or password")
            return redirect("/login")

        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            flash("Invalid email or password")
            return redirect("/login")

        # Login successful
        session["user_id"] = user[0]
        session["name"] = user[1]
        
        # Set success message
        flash("Login successful! Welcome back.")
        
        # Check if user was trying to access a specific feature
        intended_feature = request.form.get("intended_feature")
        if intended_feature:
            feature_routes = {
                'document': '/document',
                'youtube': '/youtube', 
                'webpages': '/webpages',
                'quiz': '/quiz'
            }
            return redirect(feature_routes.get(intended_feature, '/dashboard'))
        
        return redirect("/dashboard")
        
    except Exception as e:
        print(f"Login error: {e}")
        flash("Login failed. Please try again.")
        return redirect("/login")

@app.route("/signupgo", methods=["POST"])
def signupgo():
    try:
        # Get form data
        name = request.form.get("user", "").strip()
        email = request.form.get("user_email", "").strip().lower()
        mobile = request.form.get("user_mobile", "").strip()
        college = request.form.get("college", "").strip()
        branch = request.form.get("branch", "").strip()
        year = request.form.get("year", "").strip()
        language = request.form.get("language", "").strip()
        password = request.form.get("user_pass", "")
        confirm = request.form.get("user_cpass", "")

        # Basic validation
        if not all([name, email, mobile, college, branch, year, language, password, confirm]):
            flash("All fields are required")
            return redirect("/signuppage")

        if password != confirm:
            flash("Passwords do not match")
            return redirect("/signuppage")

        # Mobile validation
        if not mobile.isdigit() or len(mobile) != 10:
            flash("Mobile number must be exactly 10 digits")
            return redirect("/signuppage")

        if len(password) < 6:
            flash("Password must be at least 6 characters")
            return redirect("/signuppage")

        # Email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash("Please enter a valid email address")
            return redirect("/signuppage")

        # Database operations
        conn = get_connection()
        cur = conn.cursor()
        
        # Check if mobile already exists
        cur.execute("SELECT id FROM users WHERE mobile=%s", (mobile,))
        if cur.fetchone():
            flash("Mobile number already registered. Please use a different number.")
            conn.close()
            return redirect("/signuppage")

        # Check if email already exists
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            flash("Email already registered. Please use a different email.")
            conn.close()
            return redirect("/signuppage")

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert new user
        insert_query = """
            INSERT INTO users (full_name, email, mobile, college, branch, year, language, password) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cur.execute(insert_query, (name, email, mobile, college, branch, year, language, hashed_password))
        conn.commit()
        conn.close()
        
        flash("Registration successful! Please login with your credentials.")
        return redirect("/login")
        
    except mysql.connector.IntegrityError as e:
        if "Duplicate entry" in str(e):
            flash("Email already exists. Please use a different email.")
        else:
            flash("Registration failed. Please check your information.")
        return redirect("/signuppage")
    except Exception as e:
        print(f"Signup error: {e}")
        flash("Registration failed. Please try again.")
        return redirect("/signuppage")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT activity_type, title, description, created_at 
            FROM user_activity 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 10
        """, (session["user_id"],))
        history_rows = cur.fetchall()
        conn.close()
        
        # Convert to list of dicts
        history = []
        for row in history_rows:
            history.append({
                'activity_type': row[0],
                'title': row[1], 
                'description': row[2],
                'created_at': row[3]
            })
        
        return render_template("dashboard.html", name=session["name"], history=history)
    except Exception as e:
        print(f"Dashboard error: {e}")
        return render_template("dashboard.html", name=session["name"], history=[])

@app.route("/analyzer")
def analyzer():
    return render_template("analyzer.html")

@app.route("/document")
def document():
    if "user_id" not in session:
        return redirect("/")
    return render_template("document.html")

@app.route("/youtube")
def youtube():
    if "user_id" not in session:
        return redirect("/")
    return render_template("youtube.html")

@app.route("/webpages")
def gotowebpage():
    if "user_id" not in session:
        return redirect("/")
    return render_template("web.html")

@app.route("/quiz")
def quiz():
    if "user_id" not in session:
        return redirect("/")
    return render_template("quizess.html")

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/")
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cur.fetchone()
    conn.close()
    
    if not user:
        return redirect("/logout")
    
    # Convert tuple to dict for template
    user_dict = {
        'id': user[0],
        'full_name': user[1], 
        'email': user[2],
        'mobile': user[3],
        'college': user[4],
        'branch': user[5],
        'year': user[6],
        'language': user[7],
        'created_at': user[9] if len(user) > 9 else None
    }
    
    return render_template("profile.html", user=user_dict)

def get_youtube_video_info(video_id):
    if not YOUTUBE_API_KEY:
        return {
            "title": f"YouTube Video ({video_id})",
            "description": "YouTube API key not configured",
            "duration": "",
            "views": "",
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        }
    
    try:
        url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": video_id,
            "key": YOUTUBE_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "items" in data and len(data["items"]) > 0:
            item = data["items"][0]
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            
            duration = content.get("duration", "")
            if duration:
                match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
                if match:
                    h, m, s = match.groups()
                    h = int(h) if h else 0
                    m = int(m) if m else 0
                    s = int(s) if s else 0
                    if h > 0:
                        duration = f"{h}:{m:02d}:{s:02d}"
                    else:
                        duration = f"{m}:{s:02d}"
            
            views = stats.get("viewCount", "")
            if views:
                views = f"{int(views):,} views"
            
            return {
                "title": snippet.get("title", f"YouTube Video ({video_id})"),
                "description": snippet.get("description", "")[:200] + "..." if len(snippet.get("description", "")) > 200 else snippet.get("description", ""),
                "duration": duration,
                "views": views,
                "thumbnail": snippet.get("thumbnails", {}).get("maxres", {}).get("url", f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg")
            }
    except Exception as e:
        print(f"YouTube API error: {e}")
    
    return {
        "title": f"YouTube Video ({video_id})",
        "description": "Video information unavailable",
        "duration": "",
        "views": "",
        "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    }

def extract_video_id(url):
    if "youtube.com" in url:
        return parse_qs(urlparse(url).query).get("v", [None])[0]
    if "youtu.be" in url:
        return urlparse(url).path.replace("/", "")
    return None

# ================= PDF SUMMARY =================
@app.route("/upload-pdf-chat", methods=["POST"])
def upload_pdf_chat():
    file = request.files.get("file")
    if not file:
        return jsonify({"success": False, "error": "No file uploaded"})

    try:
        reader = PdfReader(file)
        text = "".join([p.extract_text() or "" for p in reader.pages])

        if len(text.strip()) < 100:
            return jsonify({"success": False, "error": "Scanned or empty PDF"})

        # Generate summary
        prompt = f"Summarize this PDF document in a structured format:\\n\\n{text[:4000]}"
        summary = gemini_response(prompt)
        
        return jsonify({
            "success": True,
            "filename": file.filename,
            "content": text,
            "summary": summary
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Processing failed: {str(e)}"})

@app.route("/chat-pdf", methods=["POST"])
def chat_pdf():
    data = request.get_json()
    question = data.get("question")
    pdf_content = data.get("pdf_content")
    
    if not question or not pdf_content:
        return jsonify({"success": False, "error": "Question and PDF content required"})
    
    try:
        prompt = f"Answer this question based on the PDF content:\\n\\nQuestion: {question}\\n\\nContent: {pdf_content[:4000]}"
        response = gemini_response(prompt)
        
        return jsonify({
            "success": True,
            "response": response
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ================= YOUTUBE SUMMARY =================
@app.route("/analyze-youtube", methods=["POST"])
def analyze_youtube():
    data = request.get_json()
    url = data.get("url")
    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({"success": False, "error": "Invalid YouTube URL"})

    try:
        # Get transcript
        transcript_text = None
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
            transcript_text = " ".join([t["text"] for t in transcript])
        except:
            try:
                transcript = YouTubeTranscriptApi.list_transcripts(video_id).find_generated_transcript(["en"]).fetch()
                transcript_text = " ".join([t["text"] for t in transcript])
            except:
                transcript_text = None

        # Get video info
        video_info = get_youtube_video_info(video_id)
        
        if transcript_text:
            # Generate summary
            prompt = f"Summarize this YouTube video transcript:\\n\\n{transcript_text[:4000]}"
            summary = gemini_response(prompt)
            
            return jsonify({
                "success": True,
                "title": video_info["title"],
                "description": video_info["description"],
                "thumbnail": video_info["thumbnail"],
                "duration": video_info["duration"],
                "views": video_info["views"],
                "transcript": transcript_text,
                "summary": summary,
                "has_transcript": True
            })
        else:
            return jsonify({
                "success": True,
                "title": video_info["title"],
                "description": video_info["description"],
                "thumbnail": video_info["thumbnail"],
                "duration": video_info["duration"],
                "views": video_info["views"],
                "transcript": "",
                "summary": "No transcript available for this video.",
                "has_transcript": False
            })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Analysis failed: {str(e)}"})

@app.route("/chat-youtube", methods=["POST"])
def chat_youtube():
    data = request.get_json()
    question = data.get("question")
    video_content = data.get("video_content")
    
    if not question:
        return jsonify({"success": False, "error": "Question required"})
    
    try:
        if video_content:
            prompt = f"Answer this question based on the YouTube video:\\n\\nQuestion: {question}\\n\\nVideo content: {video_content[:4000]}"
        else:
            prompt = f"Answer this general question about the video: {question}"
            
        response = gemini_response(prompt)
        
        return jsonify({
            "success": True,
            "response": response
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ================= WEBSITE SUMMARY =================
@app.route("/upload-web", methods=["POST"])
def upload_web():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url or not url.startswith("http"):
            return jsonify({"error": "Invalid website URL"}), 400
        
        print(f"Analyzing website: {url}")
        
        # Simple web scraping
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return jsonify({"error": "Could not access the website. Please check the URL."}), 400
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract images
        images = []
        try:
            img_tags = soup.find_all('img', src=True)
            for img in img_tags[:10]:  # Limit to 10 images
                src = img.get('src')
                alt = img.get('alt', '')
                
                # Convert relative URLs to absolute
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    from urllib.parse import urljoin
                    src = urljoin(url, src)
                elif not src.startswith('http'):
                    from urllib.parse import urljoin
                    src = urljoin(url, src)
                
                # Filter out small images and icons
                if not any(x in src.lower() for x in ['icon', 'logo', 'favicon', 'sprite']):
                    images.append({"src": src, "alt": alt})
        except Exception as e:
            print(f"Image extraction error: {e}")
            images = []
        
        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        content = soup.get_text(separator=" ", strip=True)
        content = re.sub(r'\\s+', ' ', content).strip()
        
        if len(content) < 200:
            return jsonify({"error": "Could not extract enough content from the website"}), 400
        
        print(f"Extracted content length: {len(content)}")
        
        # Generate summary with forced API call
        prompt = f"Create a detailed summary of this website content with headings and bullet points:\n\n{content[:3000]}"
        
        try:
            # Force API call
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                data = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                response = requests.post(url, json=data, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    summary = result["candidates"][0]["content"]["parts"][0]["text"]
                    print("Direct API call successful")
                else:
                    summary = gemini_response(prompt)
            else:
                summary = gemini_response(prompt)
        except Exception as e:
            print(f"Direct API error: {e}")
            summary = gemini_response(prompt)
        
        # Log activity
        if "user_id" in session:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO user_activity (user_id, activity_type, title, description) VALUES (%s, %s, %s, %s)",
                    (session["user_id"], "Web Analysis", f"Website: {url}", f"Analyzed website content")
                )
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Activity logging error: {e}")
        
        return jsonify({"summary": summary, "images": images})
        
    except Exception as e:
        print(f"Website analysis error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Website analysis failed. Please try again."}), 500

# ================= QUIZ GENERATION =================
@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    data = request.get_json()
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Topic required"}), 400
    
    prompt = f"""Generate exactly 30 multiple-choice questions about {topic}. 
    Format as a JSON array where each question has:
    - "question": the question text
    - "options": array of 4 answer choices (A, B, C, D)
    - "answer": the exact correct answer text (not just A/B/C/D)
    
    Example format:
    [
      {{
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "answer": "Paris"
      }}
    ]
    
    Make sure answers are educational and accurate. Return only valid JSON."""
    
    try:
        response = gemini_response(prompt)
        
        # Try to extract JSON from response
        import json
        import re
        
        # Find JSON array in response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            quiz_data = json.loads(json_str)
            
            # Validate structure
            if isinstance(quiz_data, list) and len(quiz_data) >= 10:
                # Ensure we have exactly 30 questions
                quiz_data = quiz_data[:30]
                
                # Validate each question
                valid_quiz = []
                for q in quiz_data:
                    if (isinstance(q, dict) and 
                        'question' in q and 
                        'options' in q and 
                        'answer' in q and
                        isinstance(q['options'], list) and 
                        len(q['options']) >= 4):
                        
                        # Ensure answer is in options
                        if q['answer'] not in q['options']:
                            # Try to find closest match
                            for opt in q['options']:
                                if q['answer'].lower().strip() in opt.lower().strip():
                                    q['answer'] = opt
                                    break
                        
                        valid_quiz.append(q)
                
                if len(valid_quiz) >= 10:
                    return jsonify({"quiz": valid_quiz})
        
        # Fallback: create simple quiz
        fallback_quiz = [
            {
                "question": f"What is a key concept in {topic}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A"
            }
        ] * 10
        
        return jsonify({"quiz": fallback_quiz})
        
    except Exception as e:
        print(f"Quiz generation error: {e}")
        return jsonify({"error": "Quiz generation failed"}), 500

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)