# 🎯 Intelligent AI Interview & Candidate Readiness Platform

A production-level SaaS application for AI-powered technical interview practice with Zoom-like UI, NLP evaluation, and performance analytics.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- pip

### 2. Install Dependencies

```bash
pip install streamlit scikit-learn nltk pandas numpy matplotlib plotly PyPDF2 bcrypt Pillow
```

> **Note:** `pyttsx3` and `SpeechRecognition` require system audio libraries. They are optional — the platform works fully with text input.

For voice features (optional):
```bash
# macOS
brew install portaudio espeak
pip install pyttsx3 SpeechRecognition pyaudio

# Ubuntu/Debian
sudo apt-get install portaudio19-dev espeak
pip install pyttsx3 SpeechRecognition pyaudio

# Windows: pyaudio may need a wheel — install from https://www.lfd.uci.edu/~gohlke/pythonlibs/
```

### 3. Run the App

```bash
cd interview_platform
streamlit run main.py
```

Open http://localhost:8501 in your browser.

---

## 📁 Project Structure

```
interview_platform/
├── main.py                        # Streamlit app entry point
├── requirements.txt
├── .streamlit/
│   └── config.toml                # Streamlit theme config
├── static/
│   └── styles.css                 # Zoom-like dark UI styles
└── app/
    ├── database.py                # SQLite setup & queries
    ├── auth/
    │   └── auth_manager.py        # Login, signup, session
    ├── interview/
    │   ├── question_bank.py       # 50+ questions across 5 domains
    │   └── interview_engine.py    # Session management & flow
    ├── ml_models/
    │   └── evaluator.py           # NLP scoring (TF-IDF + cosine similarity)
    └── utils/
        ├── ui_components.py       # Reusable HTML/CSS components
        ├── dashboard.py           # Charts & analytics
        └── resume_analyzer.py     # PDF resume analysis
```

---

## 🎯 Features

### 🔐 Authentication
- Signup / Login / Logout
- Bcrypt password hashing
- Session persistence via Streamlit state

### 🎙️ AI Interview Engine
- 5 domains: Python, ML, Web Dev, Data Science, DevOps
- 3 difficulty levels: Easy / Medium / Hard
- 50+ curated questions with ideal answers & keywords
- Zoom-like video call UI with AI avatar
- Live timer, question progress bar

### 🤖 NLP Evaluation (No API required)
- TF-IDF vectorization
- Cosine similarity scoring
- Keyword matching (40% weight)
- Combined scoring out of 10
- Personalized per-question feedback

### 📊 Dashboard
- Score trend chart (Plotly)
- Domain radar chart
- Difficulty distribution pie chart
- Interview history table

### 📄 Resume Analyzer
- PDF text extraction (PyPDF2)
- Skill detection across 6 domains
- Missing keyword identification
- Overall resume score (0–100)
- AI improvement suggestions

---

## 🌐 Supported Domains
| Domain | Questions |
|--------|-----------|
| Python | Easy (5), Medium (5), Hard (2) |
| Machine Learning | Easy (4), Medium (3), Hard (2) |
| Web Development | Easy (3), Medium (2), Hard (1) |
| Data Science | Easy (2), Medium (2), Hard (1) |
| DevOps | Easy (2), Medium (1), Hard (1) |

---

## 📈 Scoring System

| Score | Label |
|-------|-------|
| 80–100% | 🏆 Interview Ready |
| 60–79%  | ✅ Near Ready |
| 40–59%  | ⚠️ Needs Improvement |
| 0–39%   | ❌ Not Ready |

---

## 🔮 Extending the Platform

**Add more questions:** Edit `app/interview/question_bank.py` → `QUESTION_BANK`

**Add a new domain:**
```python
QUESTION_BANK["Blockchain"] = {
    "Easy": [{"question": "...", "keywords": [...], "ideal_answer": "..."}],
    ...
}
```

**Connect to PostgreSQL:**
In `app/database.py`, swap `sqlite3` for `psycopg2` and update `get_connection()`.

**Add voice (TTS):**
```python
import pyttsx3
engine = pyttsx3.init()
engine.say(question_text)
engine.runAndWait()
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit + Custom HTML/CSS |
| Backend | Python 3.9+ |
| Database | SQLite (→ PostgreSQL ready) |
| NLP/ML | TF-IDF, Cosine Similarity, Keyword Matching |
| Auth | bcrypt |
| Charts | Plotly |
| PDF | PyPDF2 |
| UI Theme | Custom dark CSS (Zoom-inspired) |
