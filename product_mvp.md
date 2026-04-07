# 🚀 Path to Production MVP: AI-Powered Placement Portal

This document serves as the master architectural roadmap for upgrading the Campus Placement Portal from a functional prototype into an enterprise-grade, **AI-Powered Minimum Viable Product (MVP)** ready for production deployment.

---

## 🌊 Phase 1: Core Functionality Completion
*Before scaling to algorithms, the physical infrastructure of the portal must be finalized.*

1. **Physical File Handling**
   - **Feature:** Implement encrypted PDF Resume Uploads for Students.
   - **Tech:** Flask `request.files`, `werkzeug.utils.secure_filename`, native byte reading.
2. **Search & Pagination**
   - **Feature:** Job Boards must be filterable (Location, Job Type, Salary) and paginated (10 jobs per page) to prevent server timeouts.
   - **Tech:** SQLAlchemy `.limit()`, `.offset()`, and `ilike()` SQL queries.
3. **Automated Event Triggers**
   - **Feature:** Companies must receive email notifications when a candidate applies.
   - **Tech:** `Flask-Mail` integrated with an SMTP server (like SendGrid or AWS SES).

---

## 🧠 Phase 2: AI Integration Layer
*Transforming the portal from a "dumb" database into a proactive matching engine.*

1. **Candidate Resume Parsing (OCR & NLP)**
   - **Feature:** When a student uploads a PDF, the system natively reads the document and auto-populates their profile skills, degree, and graduation year.
   - **Tech:** `PyPDF2` (for text extraction) piped directly into the `Google Gemini API` or `OpenAI API` using structured JSON output schemas to guarantee exact data extraction.
2. **Algorithmic Candidate Matching (The "Fit Score")**
   - **Feature:** Companies no longer view applications randomly. Every applicant is given a "Match Percentage %" next to their name based on how well their parsed resume matches the Job Description.
   - **Tech:** **Vector Embeddings** (SentenceTransformers) mapping the student skills vector against the job description vector to calculate **Cosine Similarity**.
3. **AI Job Description Generator**
   - **Feature:** Companies can click "Generate with AI" next to the job post box, inputting just a title (e.g. "Data Scientist"), and the AI will spin up a professional, formatted 300-word description perfectly tailored for students.

---

## ⚡ Phase 3: Modern UI/UX Upgrades 
*Matching the interface to the power of the backend.*

1. **Real-Time WebSockets (Live Status updates)**
   - **Feature:** When a company hits "Accept", the student's dashboard immediately flashes green without the student needing to hit the refresh button on their browser.
   - **Tech:** `Flask-SocketIO` utilizing continuous bi-directional event emission.
2. **Third-Party Integrations**
   - **Feature:** "Sign in with Google" / "Sign in with LinkedIn" using OAuth2 protocols to completely securely bypass password necessity.

---

## 🏭 Phase 4: Production Deployment Pipeline
*Preparing the server for the public web.*

1. **Server Fortification**
   - The default Flask development server is not secure. It must be wrapped in a production-grade **WSGI Server** like `Gunicorn` or `Waitress` (for Windows).
2. **Database Migration**
   - **SQLite** locks upon simultaneous multiple-user writes. The database must be upgraded into a hosted **PostgreSQL** instance to handle concurrent university students applying all at once.
3. **Environment Security**
   - `SECRET_KEY` and SQLite URIs must be completely removed from `config.py` and placed securely into a `.env` file handled by the `python-dotenv` library.
4. **Proxy Layering**
   - Utilizing **Nginx** as a reverse proxy to handle slow HTTP connections and serve static CSS/image assets directly so the Python backend only computes raw logic.

> By completing these 4 phases, the platform transforms from an academic project into a viable startup software product (SaaS) ready for thousands of real-world users.
