# JEE-NEET-Platform
Full-stack JEE/NEET competitive exam preparation platform built with Flask, SQLite, and Bootstrap. Features include timed tests, performance analytics, subject-wise tracking, and XP-based progression system. Pure server-side rendering with zero JavaScript.
# 🎓 JEE/NEET Competitive Exam Platform

A comprehensive exam preparation platform for JEE and NEET aspirants, built using Python Flask with a pure server-side architecture.

## ✨ Features

- **🔐 User Authentication** - Secure registration and login system
- **📝 Timed Exams** - Server-side timer with auto-submit functionality
- **📊 Performance Analytics** - Subject-wise performance tracking and analytics
- **🎯 Smart Scoring** - +4/-1 marking scheme with detailed result breakdown
- **📈 Progress Tracking** - XP and leveling system to track improvement
- **💪 Strength/Weakness Analysis** - Chapter-wise performance identification
- **📱 Responsive Design** - Works on desktop, tablet, and mobile devices
- **🎨 Modern UI** - Clean, professional interface with Bootstrap 5

## 🛠️ Tech Stack

- **Backend:** Python, Flask 3.0.0
- **Database:** SQLite (programmatic creation via SQLAlchemy ORM)
- **Frontend:** Jinja2, HTML5, CSS3, Bootstrap 5
- **Authentication:** Flask-Login
- **JavaScript:** None (pure server-side rendering)

## 📋 Key Highlights

- ✅ **No JavaScript** - All functionality implemented server-side
- ✅ **Programmatic Database** - Tables created via SQLAlchemy models
- ✅ **5 Database Models** - User, Question, TestAttempt, Answer, SubjectAnalytics
- ✅ **Session Management** - Flask sessions for exam state
- ✅ **RESTful Routes** - Clean URL structure with proper HTTP methods

## 🚀 Quick Start
```bash
# Clone repository
git clone https://github.com/yourusername/jee-neet-platform.git
cd jee-neet-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Access at: `http://127.0.0.1:5000`

## 📂 Project Structure
```
jee-neet-platform/
├── app.py                 # Main application & routes
├── models.py             # Database models
├── config.py             # Configuration settings
├── utils.py              # Helper functions
├── requirements.txt      # Dependencies
├── templates/            # Jinja2 templates
│   ├── base.html
│   ├── dashboard.html
│   ├── exam.html
│   └── results.html
├── static/               # CSS, images
│   ├── style.css
│   └── images/
└── instance/             # SQLite database (auto-created)
```

## 🎓 Academic Project

Developed as part of Modern Application Development (MAD1) course requirements:
- Pure Flask backend with no client-side JavaScript
- Programmatic database creation (no manual tools)
- Local deployment compatible
- All MAD1 framework requirements met

## 📊 Database Schema

- **User** - Authentication, profile, XP/level tracking
- **Question** - Exam questions with multiple choice options
- **TestAttempt** - User exam attempts with scores
- **Answer** - Individual question responses
- **SubjectAnalytics** - Performance metrics per subject

## 🔒 Security Features

- Password hashing with Werkzeug
- SQL injection prevention via SQLAlchemy ORM
- Session-based authentication
- CSRF protection

## 📄 License

MIT License - Feel free to use for educational purposes

## 👨‍💻 Author

[Your Name] - MAD1 Project, IIT Madras

## 🙏 Acknowledgments

Built as part of IIT Madras BS Degree in Data Science and Applications
