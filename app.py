from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Company, Student, Job, Application
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    # Auto-create admin user on first run
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)
        db.session.commit()

# ====== AUTH ROUTES ====== #

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'company':
                return redirect(url_for('company_dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student_dashboard'))
        flash("Invalid username or password", "danger")
    
    # We can route admin to admin_login specifically, but one login is cleaner.
    # To strictly follow instructions, we may have a separate login if needed, or use the single one.
    return render_template('admin_login.html') 

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        description = request.form.get('description')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register_company'))
            
        user = User(username=username, password=generate_password_hash(password), role='company')
        db.session.add(user)
        db.session.flush() # get user id
        
        company = Company(user_id=user.id, name=name, description=description)
        db.session.add(company)
        db.session.commit()
        
        flash("Registration successful! Please wait for Admin approval.", "success")
        return redirect(url_for('login'))
        
    return render_template('company_register.html')

@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        degree = request.form.get('degree')
        skills = request.form.get('skills')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register_student'))
            
        user = User(username=username, password=generate_password_hash(password), role='student')
        db.session.add(user)
        db.session.flush()
        
        student = Student(user_id=user.id, name=name, degree=degree, skills=skills)
        db.session.add(student)
        db.session.commit()
        
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))
        
    return render_template('student_register.html')

# ====== ADMIN ROUTES ====== #

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    companies = Company.query.all()
    students = Student.query.all()
    return render_template('admin_dashboard.html', companies=companies, students=students)

@app.route('/admin/approve/<int:company_id>')
@login_required
def approve_company(company_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
    company = Company.query.get_or_404(company_id)
    company.is_approved = True
    db.session.commit()
    flash(f"Company {company.name} approved!", "success")
    return redirect(url_for('admin_dashboard'))

# ====== COMPANY ROUTES ====== #

@app.route('/company/dashboard', methods=['GET', 'POST'])
@login_required
def company_dashboard():
    if current_user.role != 'company':
        return "Unauthorized", 403
    
    company = current_user.company_profile
    if not company.is_approved:
        return "Your account is pending admin approval.", 403
        
    if request.method == 'POST':
        # Add new Job
        title = request.form.get('title')
        description = request.form.get('description')
        new_job = Job(company_id=company.id, title=title, description=description)
        db.session.add(new_job)
        db.session.commit()
        flash("Job posted successfully!", "success")
        return redirect(url_for('company_dashboard'))
        
    jobs = Job.query.filter_by(company_id=company.id).all()
    # List of tuples (Job, Application) to display
    applications = Application.query.join(Job).filter(Job.company_id == company.id).all()
    
    return render_template('company_dashboard.html', company=company, jobs=jobs, applications=applications)

@app.route('/company/job/update_status/<int:app_id>/<status>')
@login_required
def update_application_status(app_id, status):
    if current_user.role != 'company':
        return "Unauthorized", 403
    application = Application.query.get_or_404(app_id)
    
    # Must own the job
    if application.job.company_id != current_user.company_profile.id:
        return "Unauthorized", 403
        
    if status in ['Accepted', 'Rejected']:
        application.status = status
        db.session.commit()
        flash(f"Application marked as {status}!", "success")
        
    return redirect(url_for('company_dashboard'))

# ====== STUDENT ROUTES ====== #

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return "Unauthorized", 403
    student = current_user.student_profile
    applications = Application.query.filter_by(student_id=student.id).all()
    return render_template('student_dashboard.html', student=student, applications=applications)

@app.route('/student/jobs')
@login_required
def browse_jobs():
    if current_user.role != 'student':
        return "Unauthorized", 403
    jobs = Job.query.all()
    return render_template('browse_jobs.html', jobs=jobs)

@app.route('/student/apply/<int:job_id>')
@login_required
def apply_job(job_id):
    if current_user.role != 'student':
        return "Unauthorized", 403
    
    job = Job.query.get_or_404(job_id)
    student = current_user.student_profile
    
    # Check if already applied
    existing = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
    if existing:
        flash("You have already applied for this job.", "warning")
    else:
        app = Application(student_id=student.id, job_id=job.id)
        db.session.add(app)
        db.session.commit()
        flash(f"Successfully applied to {job.title} at {job.company.name}!", "success")
        
    return redirect(url_for('student_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
