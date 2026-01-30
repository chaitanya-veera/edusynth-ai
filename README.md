# 📘 EduSynth AI - AI-Powered Educational Platform

An intelligent educational platform that transforms content into actionable learning experiences using advanced NLP and AI technologies.

## 🚀 Features

### 📄 PDF Document Analysis
- Upload and process PDF documents
- AI-powered chatbot for document Q&A with RAG implementation
- Intelligent content extraction and summarization
- PDF summary download functionality
- ChatGPT-like structured response formatting

### 🎥 YouTube Video Analysis
- Analyze YouTube videos with transcript extraction
- Generate comprehensive video summaries
- Interactive chatbot for video content discussion
- Support for videos with and without transcripts
- Real video information display (title, description, views, duration)

### 🌐 Web Content Summarization
- Extract and summarize website content
- Image extraction and display from web pages
- Structured summary generation with professional formatting
- Smart content parsing with multiple API fallbacks

### 🧠 AI Quiz Generation
- Generate custom quizzes on any topic (30 questions)
- Pagination system (5 questions per page, 6 pages total)
- Multiple choice format with instant feedback
- Submit button appears only after all questions answered
- Green/red color coding for correct/wrong answers
- Always shows correct answer when user selects wrong option

### 👤 User Management
- Secure user authentication with bcrypt
- Email validation and password requirements
- OTP-based password reset system
- User profile with real database information
- Change password functionality
- Activity history tracking and display

### 📱 Mobile Responsive Design
- Hamburger navigation menu for all pages
- Fully responsive design for all screen sizes
- Touch-friendly interface
- Consistent mobile experience across all features

## 🛠️ Technology Stack

### Backend
- **Flask** - Python web framework
- **MySQL** - Database management
- **Google Gemini AI** - Natural language processing
- **bcrypt** - Password hashing
- **PyPDF2** - PDF processing
- **ReportLab** - PDF generation for summaries
- **BeautifulSoup** - Web scraping
- **NLTK** - Natural language toolkit

### Frontend
- **HTML5/CSS3** - Modern responsive design
- **JavaScript** - Interactive functionality
- **Poppins & Inter** - Google Fonts
- **Mobile-First Design** - Responsive hamburger navigation

### APIs & Services
- **Google Gemini API** - AI text generation
- **YouTube Data API** - Video information
- **YouTube Transcript API** - Transcript extraction
- **Gmail SMTP** - Email services for OTP
- **Web Scraping APIs** - Content extraction with fallbacks

## 📋 Prerequisites

- Python 3.7+
- MySQL Server
- Google Gemini API Key
- YouTube Data API Key (optional)
- Gmail App Password (for OTP emails)

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/edusynth-ai.git
   cd edusynth-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   YOUTUBE_API_KEY=your_youtube_api_key_here
   SMTP_EMAIL=your_gmail_address
   SMTP_PASSWORD=your_gmail_app_password
   ```

4. **Set up MySQL database**
   ```sql
   CREATE DATABASE edusynth_ai;
   USE edusynth_ai;
   
   CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       full_name VARCHAR(255) NOT NULL,
       email VARCHAR(255) UNIQUE NOT NULL,
       mobile VARCHAR(20),
       college VARCHAR(255),
       branch VARCHAR(255),
       year VARCHAR(50),
       language VARCHAR(50),
       password VARCHAR(255) NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   
   CREATE TABLE user_activity (
       id INT AUTO_INCREMENT PRIMARY KEY,
       user_id INT,
       activity_type VARCHAR(50),
       title VARCHAR(500),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES users(id)
   );
   ```

5. **Configure database connection**
   Update `db.py` with your MySQL credentials:
   ```python
   def get_connection():
       return mysql.connector.connect(
           host="localhost",
           user="your_username",
           password="your_password",
           database="edusynth_ai"
       )
   ```

## 🚀 Running the Application

### Local Development
1. **Start the Flask application**
   ```bash
   python app.py
   ```

2. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

### Deploy on Render

1. **Create Render Account**
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub account

2. **Create Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure deployment settings:
     ```
     Build Command: pip install -r requirements.txt
     Start Command: python app.py
     ```

3. **Set Environment Variables**
   Add these in Render dashboard:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   YOUTUBE_API_KEY=your_youtube_api_key_here
   SMTP_EMAIL=your_gmail_address
   SMTP_PASSWORD=your_gmail_app_password
   DATABASE_URL=your_mysql_connection_string
   ```

4. **Database Setup**
   - Use Render's PostgreSQL or external MySQL service
   - Update `db.py` for production database connection
   - Run database migrations after deployment

5. **Deploy**
   - Push code to GitHub
   - Render automatically builds and deploys
   - Access your app at `https://your-app-name.onrender.com`

## 📁 Project Structure

```
edusynth-ai/
├── app.py                 # Main Flask application
├── db.py                  # Database connection
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── README.md             # Project documentation
└── templates/            # HTML templates
    ├── index.html        # Landing page
    ├── about.html        # About page
    ├── login.html        # Login page
    ├── signup.html       # Registration page
    ├── forget.html       # Password reset
    ├── dashboard.html    # User dashboard
    ├── document.html     # PDF analysis
    ├── youtube.html      # YouTube analysis
    ├── web.html          # Web content analysis
    ├── quizess.html      # Quiz generation
    └── profile.html      # User profile
```

## 🔧 Configuration

### API Keys Setup

1. **Google Gemini API**
   - Visit [Google AI Studio](https://ai.google.dev/)
   - Generate API key
   - Add to `.env` file

2. **YouTube Data API** (Optional)
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Enable YouTube Data API v3
   - Create credentials and add to `.env`

3. **Gmail SMTP** (For OTP emails)
   - Enable 2-factor authentication on Gmail
   - Generate app password
   - Add credentials to `.env`

## 🎯 Usage

### For Students
1. **Register** with email and academic details
2. **Upload PDFs** for AI-powered analysis and download summaries
3. **Analyze YouTube videos** for educational content
4. **Summarize websites** for research with image extraction
5. **Generate quizzes** (30 questions) for self-assessment
6. **Chat with AI** about uploaded content
7. **Track activity** through dashboard history

### For Educators
1. **Create accounts** for institutional use
2. **Process educational materials** efficiently
3. **Generate assessments** automatically
4. **Download PDF summaries** for distribution
5. **Track learning progress** through dashboard

## 🔒 Security Features

- **Password Requirements**: 6+ characters with uppercase, lowercase, numbers, and symbols
- **Email Validation**: Automatic lowercase conversion and format validation
- **OTP System**: Secure password reset with time-limited codes
- **Session Management**: Secure user sessions with Flask
- **Input Sanitization**: Protection against common web vulnerabilities
- **Duplicate Prevention**: Email and mobile number uniqueness validation

## 🎨 Design Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Clean, professional interface with orange theme
- **Hamburger Navigation**: Mobile-friendly navigation on all pages
- **Consistent Branding**: Orange (#f59e0b) theme throughout
- **Accessibility**: User-friendly navigation and interactions
- **Loading States**: Visual feedback for all operations
- **Structured Formatting**: ChatGPT-like response formatting

## 📊 AI Capabilities

### Simple RAG Implementation
- **Keyword-based retrieval** for document Q&A
- **Chunk-based processing** for large documents
- **Relevance scoring** for accurate responses
- **Context-aware** question answering

### Content Processing
- **PDF text extraction** with error handling
- **YouTube transcript processing** with fallback options
- **Web content parsing** with image extraction
- **Structured summary generation** with professional formatting
- **Quiz generation** with intelligent question creation

### Enhanced Features
- **PDF Summary Download** - Generate and download PDF summaries
- **Activity Tracking** - Monitor user interactions and history
- **Mobile Optimization** - Full responsive design with hamburger menus
- **Real-time Feedback** - Instant quiz results with color coding

## 🐛 Troubleshooting

### Common Issues

1. **API Quota Exceeded**
   - Gemini API has 20 requests/day limit on free tier
   - Upgrade to paid plan or wait for quota reset

2. **Database Connection Error**
   - Check MySQL server status
   - Verify credentials in `db.py`
   - Ensure both users and user_activity tables exist

3. **Email Not Sending**
   - Verify Gmail app password
   - Check SMTP settings in `.env`

4. **PDF Processing Failed**
   - Ensure PDF contains extractable text
   - Check file size limitations

5. **Mobile Navigation Issues**
   - Clear browser cache
   - Ensure JavaScript is enabled

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - Veera Chaitanya - [YourGitHub](https://github.com/chaitanya-veera)

## 🙏 Acknowledgments

- Google Gemini AI for natural language processing
- YouTube API for video data access
- Flask community for the excellent framework
- ReportLab for PDF generation capabilities
- All contributors and testers

## 📞 Support

For support, email support@edusynth-ai.com or create an issue in the GitHub repository.

---

**EduSynth AI** - Transforming Education with Artificial Intelligence 🚀