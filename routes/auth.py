from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, CompanyProfile, StudentProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'danger')
                return redirect(url_for('auth.login'))
            
            if user.role == 'company':
                profile = CompanyProfile.query.filter_by(user_id=user.id).first()
                if profile.approval_status != 'Approved':
                    flash('Your company registration is pending admin approval.', 'warning')
                    return redirect(url_for('auth.login'))
            
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'company':
                return redirect(url_for('company.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        contact = request.form.get('contact')
        cgpa = request.form.get('cgpa')
        department = request.form.get('department')
        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('auth.register_student'))
        
        new_user = User(username=username, email=email, password=generate_password_hash(password), role='student')
        db.session.add(new_user)
        db.session.flush()
        
        student_profile = StudentProfile(user_id=new_user.id, name=name, contact=contact, cgpa=cgpa, department=department)
        db.session.add(student_profile)
        db.session.commit()
        
        flash('Student registration successful. Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register_student.html')

@auth_bp.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        hr_contact = request.form.get('hr_contact')
        website = request.form.get('website')
        description = request.form.get('description')
        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('auth.register_company'))
        
        new_user = User(username=username, email=email, password=generate_password_hash(password), role='company')
        db.session.add(new_user)
        db.session.flush()
        
        company_profile = CompanyProfile(user_id=new_user.id, name=name, hr_contact=hr_contact, website=website, description=description)
        db.session.add(company_profile)
        db.session.commit()
        
        flash('Company registration submitted. Wait for admin approval.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register_company.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
