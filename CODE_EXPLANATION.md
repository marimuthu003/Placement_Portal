# 🛠️ System Design & Full Code Walkthrough

This document breaks down the **System Design** of your Campus Placement Portal, followed by an in-depth, line-by-line explanation of your Python backend files (`config.py`, `models.py`, and `app.py`).

---

## 1. System Design Architecture

Your application follows the **MVC (Model-View-Controller)** design pattern:
1. **Model (`models.py`)**: The data layer. It defines how data (Users, Jobs) is structured and saved in the SQLite database.
2. **View (`templates/` folder)**: The presentation layer. The HTML and CSS files that the user actually sees on their screen.
3. **Controller (`app.py`)**: The logic layer (The "Traffic Cop"). It receives a user's web request, enforces permissions, fetches required data from the database (*Model*), and hands it to the *View*.

**Key Technology Stack:**
- **Flask**: The web framework that receives URL requests and runs the Controller logic.
- **Flask-SQLAlchemy (ORM)**: Translates Python code into SQL database commands automatically, so you don't have to write raw complex SQL queries.
- **Flask-Login**: Manages user session cookies securely so the server remembers who is logged in across different pages.

---

## 2. The Configuration (`config.py`)

This file sets up the hidden environment tools for your application.

```python
import os

class Config:
    # 1. SECRET_KEY is used by Flask to encrypt your users' login sessions (cookies) securely. 
    # It tries to find a secret key in your system, or defaults to the string below.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-placement-key'
    
    # 2. This tells SQLAlchemy exactly where to build and find your database file. 
    # 'sqlite:///' means it's a local file. 'placement.db' is the filename.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///placement.db'
    
    # 3. Turns off a feature that tracks every modification to the database. 
    # It consumes a lot of memory, so we disable it for better performance.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

## 3. The Database Blueprint (`models.py`)

This file contains "Classes". A Python Class here represents exactly one Table in your SQLite database.

```python
# Import the tools we need to talk to the database and manage logins
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize the SQLAlchemy object which acts as our bridge to the database.
db = SQLAlchemy()

# == TABLE 1: USER ==
# UserMixin gives this class built-in login properties (like `is_authenticated`)
class User(UserMixin, db.Model):
    # db.Column creates a column in the database table.
    id = db.Column(db.Integer, primary_key=True) # A unique ID number for every user
    username = db.Column(db.String(80), unique=True, nullable=False) # Must be unique, cannot be empty
    password = db.Column(db.String(255), nullable=False) # Encrypted password storage
    role = db.Column(db.String(20), nullable=False) # Will contain either 'admin', 'company', or 'student'
    
    # Relationships connect this base User table to the Company and Student tables automatically
    company_profile = db.relationship('Company', backref='user', uselist=False)
    student_profile = db.relationship('Student', backref='user', uselist=False)

# == TABLE 2: COMPANY ==
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # This ForeignKey says: "The user_id here must match an 'id' in the base User table"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True) # Optional long text feature
    is_approved = db.Column(db.Boolean, default=False) # Starts as false, Admin changes to True
    
    # One company can post many jobs. This links them together globally.
    jobs = db.relationship('Job', backref='company', lazy=True)

# == TABLE 3: STUDENT ==
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.String(255), nullable=True)
    
    # One student can have multiple applications globally.
    applications = db.relationship('Application', backref='student', lazy=True)

# == TABLE 4: JOB ==
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # Auto-saves the exact timestamp
    applications = db.relationship('Application', backref='job', lazy=True)

# == TABLE 5: APPLICATION (The Bridge between Job and Student) ==
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending') # Default word is 'Pending'
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 4. The Core Logic (`app.py`)

This file runs the actual server and handles every URL link that anyone enters. I have explained chunk by chunk.

### Part A: Setup and Initial Configurations
```python
# Import the tools we need from Flask and our own files
from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Company, Student, Job, Application
from config import Config

# Create the flask app instance 
app = Flask(__name__)
# Load our configuration from config.py 
app.config.from_object(Config)

# Link our database tools to this running app
db.init_app(app)

# Setup LoginManager to handle user login sessions automatically
login_manager = LoginManager(app)
# If an unauthorized user tries to view a restricted page, send them to the 'login' route
login_manager.login_view = 'login'

# This function helps Flask-login fetch the current user's profile from the database based on their ID cookie
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Generate database tables before the application accepts its first request
with app.app_context():
    db.create_all() # Triggers SQLite to build all tables from models.py
    
    # Auto-create admin user on first run if it doesn't already exist
    if not User.query.filter_by(role='admin').first():
        # Hash the password so it's unreadable in the database, then save it
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        db.session.add(admin) # Queues the insert
        db.session.commit() # Saves the insert to the hard drive
```

### Part B: Authentication Routes (Logging in and Registering)
```python
# @app.route defines the URL path. '/' is the homepage.
@app.route('/')
def index():
    return render_template('index.html') # Sends the index.html file to the user's browser

# Methods GET (viewing the page) and POST (submitting a form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # If the user clicked "Submit"
        # Grab what they typed in the text boxes
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Search the database for that exact username
        user = User.query.filter_by(username=username).first()
        
        # If user exists AND the typed password matches the encrypted hash saved inside the database
        if user and check_password_hash(user.password, password):
            login_user(user) # Log them in formally and generate the cookie
            
            # Send them to different dashboards based on their role setup automatically
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'company':
                return redirect(url_for('company_dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student_dashboard'))
                
        # If password failed, show a red error banner at the top of the screen next load
        flash("Invalid username or password", "danger")
    
    # If the user just visited the page normally (GET), show the HTML login form
    return render_template('admin_login.html') 

@app.route('/logout')
@login_required # Cannot logout if not logged in
def logout():
    logout_user() # Destroys the session cookie
    return redirect(url_for('index')) # Send back to home page

@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        # Same logic: grab form data elements
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Stop them if the username is taken
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register_company'))
            
        # 1. Create the base User
        user = User(username=username, password=generate_password_hash(password), role='company')
        db.session.add(user)
        db.session.flush() # flush() gets the new user.id without permanently writing to disk yet
        
        # 2. Create the associated Company profile giving it the newly generated user ID
        company = Company(user_id=user.id, name=name, description=description)
        db.session.add(company)
        db.session.commit() # Save BOTH to database permanently
        
        flash("Registration successful! Please wait for Admin approval.", "success")
        return redirect(url_for('login'))
        
    return render_template('company_register.html')
    
# NOTE: The student registration code looks and functions almost identically to the Company registration 
# but inserts into the Student database table instead and does not require admin approval.
```

### Part C: Company Dashboard & Functionality
```python
@app.route('/company/dashboard', methods=['GET', 'POST'])
@login_required # Forces user to be logged in
def company_dashboard():
    # If a student or admin navigates here via URL directly, stop them dead
    if current_user.role != 'company':
        return "Unauthorized", 403
    
    # Retrieve this exact company's detailed profile using the relationship defined in models.py
    company = current_user.company_profile
    
    # Has the admin approved them? If not, stop them.
    if not company.is_approved:
        return "Your account is pending admin approval.", 403
        
    # If they are submitting the "Post Job" form inside the dashboard
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        # Create new Job and link it to this company
        new_job = Job(company_id=company.id, title=title, description=description)
        db.session.add(new_job) # Stage the insertion
        db.session.commit() # Write the insertion permanently
        flash("Job posted successfully!", "success")
        return redirect(url_for('company_dashboard')) # Refresh the page to show new job
        
    # GET Phase: Prepare data to show the HTML template
    # Ask Database: "Give me all Jobs where company ID matches this current company instance"
    jobs = Job.query.filter_by(company_id=company.id).all()
    
    # Advanced Database Join! "Merge the Application table and Job table. Isolate any Applications 
    # connected to Jobs that belong ONLY to my company id."
    applications = Application.query.join(Job).filter(Job.company_id == company.id).all()
    
    # Hand off all the fetched variable data to company_dashboard.html so Jinja can loop through it
    return render_template('company_dashboard.html', company=company, jobs=jobs, applications=applications)

@app.route('/company/job/update_status/<int:app_id>/<status>')
@login_required
def update_application_status(app_id, status):
    # This route handles clicks when Company selects "Accept" or "Reject". 
    # Example URL processed: /company/job/update_status/5/Accepted
    
    if current_user.role != 'company':
        return "Unauthorized", 403
        
    # Fetch that exact application row by its ID
    application = Application.query.get_or_404(app_id) # 404 error if it doesn't exist
    
    # Security block: Only allow modifying it if the company actually OWNS the job this user applied to
    if application.job.company_id != current_user.company_profile.id:
        return "Unauthorized", 403
        
    if status in ['Accepted', 'Rejected']:
        application.status = status # Update RAM memory
        db.session.commit() # Write update to database on hard drive
        flash(f"Application marked as {status}!", "success")
        
    return redirect(url_for('company_dashboard'))
```

### Part D: Core Student Actions
```python
@app.route('/student/apply/<int:job_id>')
@login_required
def apply_job(job_id):
    # When a student clicks "Apply" on a job listed in the feed...
    if current_user.role != 'student':
        return "Unauthorized", 403
    
    job = Job.query.get_or_404(job_id)
    student = current_user.student_profile
    
    # Search Database: Look to see if this student already has an application for this EXACT job
    existing = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
    
    # If they do, deny the action so they cannot spam applications
    if existing:
        flash("You have already applied for this job.", "warning")
    else:
        # Construct a new blank Application connecting the student.id and job.id
        app = Application(student_id=student.id, job_id=job.id)
        db.session.add(app)
        db.session.commit()
        flash(f"Successfully applied to {job.title} at {job.company.name}!", "success")
        
    return redirect(url_for('student_dashboard'))
```
