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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                activity_type ENUM('PDF', 'YouTube', 'Website', 'Quiz') NOT NULL,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Table creation error: {e}")

create_tables()

# Routes
@app.route("/")
def landing():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signuppage")
def signuppage():
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/logingo", methods=["POST"])
def logingo():
    email = request.form["user_email"]
    password = request.form["user_pass"]

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        flash("Invalid credentials")
        return redirect("/login")

    session["user_id"] = user["id"]
    session["name"] = user["full_name"]
    return redirect("/dashboard")

@app.route("/signupgo", methods=["POST"])
def signupgo():
    name = request.form["user"]
    email = request.form["user_email"]
    mobile = request.form["user_mobile"]
    college = request.form["college"]
    branch = request.form["branch"]
    year = request.form["year"]
    language = request.form["language"]
    password = request.form["user_pass"]
    confirm = request.form["user_cpass"]

    if password != confirm:
        flash("Passwords do not match")
        return redirect("/signuppage")

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT email FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        flash("Email already registered. Please use different email.")
        conn.close()
        return redirect("/signuppage")

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    cur.execute(
        "INSERT INTO users (full_name, email, mobile, college, branch, year, language, password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (name, email, mobile, college, branch, year, language, hashed)
    )
    conn.commit()
    conn.close()

    flash("Registration successful")
    return redirect("/login")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT activity_type, title, description, created_at 
        FROM user_activity 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT 10
    """, (session["user_id"],))
    history = cur.fetchall()
    conn.close()
    
    return render_template("dashboard.html", name=session["name"], history=history)

@app.route("/document")
def document():
    return render_template("document.html")

@app.route("/youtube")
def youtube():
    return render_template("youtube.html")

@app.route("/webpages")
def gotowebpage():
    return render_template("web.html")

@app.route("/quiz")
def quiz():
    return render_template("quizess.html")

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/")
    
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cur.fetchone()
    conn.close()
    
    if not user:
        return redirect("/logout")
    
    return render_template("profile.html", user=user)

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
        
        # Simple web scraping
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        content = soup.get_text(separator=" ", strip=True)
        content = re.sub(r'\\s+', ' ', content).strip()
        
        if len(content) < 200:
            return jsonify({"error": "Could not extract enough content"}), 400
        
        # Generate summary
        prompt = f"Summarize this website content:\\n\\n{content[:4000]}"
        summary = gemini_response(prompt)
        
        return jsonify({"summary": summary})
        
    except Exception as e:
        return jsonify({"error": f"Website analysis failed: {str(e)}"}), 500

# ================= QUIZ GENERATION =================
@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    data = request.get_json()
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Topic required"}), 400
    
    prompt = f"Generate 10 multiple-choice questions about {topic}. Format as JSON with question, options array, and correct answer index."
    
    try:
        response = gemini_response(prompt)
        return jsonify({"quiz": response})
    except Exception as e:
        return jsonify({"error": "Quiz generation failed"}), 500

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)