# Campus Placement Portal 🎓🚀

A truly modern, functional, and automated Campus Placement Portal built natively using **Python**, **Flask**, and **SQLite**. It features a sophisticated Vanilla CSS UI (Warm Sunrise Gradients & Glassmorphism) and fully handles secure interactions between Admins, Companies, and Students.

## ✨ Features
- **Multi-Tier Authorization:** Distinct workflows for Admins, Companies, and Students natively handled without framework bloat.
- **Verification Workflows:** New Companies are automatically marked as "Pending" and must be manually verified by the Admin to ensure safety.
- **Job Ecosystem:** Companies can post job openings while Students can browse a dynamically rendered job board.
- **Application Tracking:** Students apply with a single click, and Companies can instantly review, Accept, or Reject those candidates on their personalized dashboard.
- **Premium UI/UX:** A fast, animated, accessible interface built completely with Vanilla HTML/CSS. 

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/marimuthu003/YOUR-REPO-NAME.git
   cd YOUR-REPO-NAME
   ```

2. **Activate the Virtual Environment:**
   *(Windows)*
   ```bash
   .\venv\Scripts\Activate.ps1
   ```
   *(Mac/Linux)*
   ```bash
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Application:**
   ```bash
   python app.py
   ```

*(Note: The database (`placement.db`) and a default Admin account (`username: admin`, `password: admin123`) will automatically be generated the first time you run the server).*
