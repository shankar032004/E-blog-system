# ✍️ iBlog — AI-Powered E-Blog System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-black?logo=flask)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red)](https://www.sqlalchemy.org/)
[![NLTK](https://img.shields.io/badge/NLP-NLTK%20%2B%20TextBlob-green)](https://www.nltk.org/)

**iBlog (E-Blog System)** is a full-stack Flask blogging platform enhanced with built-in **NLP & Speech-to-Text AI tools**—including voice-to-text blog dictation, extractive text summarization, grammar/spelling auto-correction, and multi-language translation—backed by SQLite and JWT authentication.

---

## ✨ Key Features

### 📝 Core Blogging Platform
- **User Authentication:** Account registration and login with **Flask-Bcrypt** password hashing and **PyJWT** (24-hour HS256 tokens).
- **Rich Blog Publishing:** Create, browse, and read full blog posts with categories, author attribution, view-count tracking, and pre-seeded sample articles.
- **Full-Text Search:** Search across blog titles, content, categories, and author names (`/search`, `/api/search_blogs`).

### 🤖 Built-In AI & NLP Utilities
- **Voice-to-Text Dictation (`/voice-to-text`):** Converts uploaded `.wav`, `.webm`, and `.ogg` audio recordings into text using `SpeechRecognition` (Google Speech API with Sphinx fallback) and `pydub` format conversion.
- **Extractive Text Summarization (`/api/summarize`):** Word-frequency sentence scoring using `NLTK` (`punkt`, `stopwords`) to produce concise summaries.
- **Auto-Correction & Spelling Suggestions (`/api/correct_text`):** Grammar and spelling correction powered by `TextBlob` with per-word suggestion mapping.
- **Multi-Language Translation (`/api/translate`):** Automatic source-language detection and translation via `deep-translator` (`GoogleTranslator`).

---

## 📂 Repository Structure

```text
E-blog-system/
├── README.md                  # Project overview & run instructions
├── PROJECT_REPORT.md          # Detailed technical architecture & API report
├── PROJECT_INFO.txt           # Original project summary notes
├── .gitignore                 # Excludes instance/, *.db, *.wav, __pycache__, .env, venv
├── .env.example               # Environment variable template
├── server.py                  # Main Flask application, ORM models & NLP/API endpoints
├── requirements.txt           # Python package dependencies
└── templates/                 # Responsive HTML5/CSS3/JS Jinja2 templates
    ├── index.html             # Landing page
    ├── login.html             # User sign-in page
    ├── signup.html            # User registration with password strength meter
    ├── blogpost.html          # All blogs listing & category view
    ├── blog_detail.html       # Single blog reader with translate & summarize tools
    ├── create_blog.html       # Blog editor with AI auto-correct, translate & summarize
    └── search.html            # Live blog search page
```

---

## 🚀 Run Commands (Quick Start)

### Prerequisites
- **Python 3.8+**
- **pip**
- *(Optional for non-WAV voice uploads)* **FFmpeg** installed on system PATH (required by `pydub` for `.webm`/`.ogg` conversion)

### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SECRET_KEY="your_secret_key_here"
python server.py
```

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="your_secret_key_here"
python server.py
```

- Access the application at **`http://127.0.0.1:5000/`**
- On first startup, `init_db()` automatically creates the SQLite database (`instance/blog.db`) and seeds **5 sample blog posts**.

---

## 🔧 API Endpoints Summary

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/signup` | Register a new user (Bcrypt-hashed password) |
| **Auth** | `POST` | `/api/login` | Authenticate user and return 24h JWT token |
| **Blogs** | `POST` | `/api/add_blog` | Create and publish a new blog post |
| **Blogs** | `GET` | `/api/get_blogs` | Retrieve all blogs (newest first, 200-char preview) |
| **Blogs** | `GET` | `/api/get_blog/<id>` | Fetch full blog post & increment view counter |
| **Blogs** | `GET` | `/api/search_blogs?q=` | Search blogs by title, content, category, or author |
| **NLP** | `POST` | `/api/translate` | Translate text to target language (`GoogleTranslator`) |
| **NLP** | `POST` | `/api/summarize` | Generate extractive summary (`NLTK`) |
| **NLP** | `POST` | `/api/correct_text` | Spelling auto-correction + word suggestions (`TextBlob`) |
| **Speech** | `POST` | `/voice-to-text` | Transcribe uploaded audio file to text |

---

## 📄 Detailed Technical Report

For the complete architecture diagram, database schema, NLP algorithm walkthrough, security notes, and known edge cases, see **[PROJECT_REPORT.md](./PROJECT_REPORT.md)**.
