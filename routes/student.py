import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import re
from models import db, StudentProfile, PlacementDrive, Application

student_bp = Blueprint('student', __name__)

def student_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    # Base query: Only show approved drives that haven't passed the deadline
    query = PlacementDrive.query.filter(PlacementDrive.status == 'Approved', PlacementDrive.deadline >= datetime.utcnow())
    
    # Frontend Filtering Logic
    filter_keyword = request.args.get('keyword')
    if filter_keyword:
        search = f"%{filter_keyword}%"
        query = query.filter(PlacementDrive.job_title.ilike(search) | PlacementDrive.job_description.ilike(search) | PlacementDrive.eligibility_criteria.ilike(search))
        
    drives = query.all()
    
    # AI / Recommendation Layer (Advanced Feature)
    for drive in drives:
        drive.is_recommended = False
        # Extract CGPA requirements from text e.g. "7.5 CGPA"
        cgpa_match = re.search(r'(\d\.?\d*)\s*(?:cgpa|gpa)', drive.eligibility_criteria.lower())
        if cgpa_match:
            required_cgpa = float(cgpa_match.group(1))
            if profile.cgpa >= required_cgpa:
                drive.is_recommended = True
        elif profile.department.lower() in drive.eligibility_criteria.lower() or profile.department.lower() in drive.job_description.lower():
            # If department strictly matched
            drive.is_recommended = True
            
    # Get dict of applied drive mapping {drive_id: status}
    applied_drives = {app.drive_id: app.status for app in profile.applications}
    
    return render_template('student/dashboard.html', profile=profile, drives=drives, applied_drives=applied_drives)

@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        profile.name = request.form.get('name')
        profile.contact = request.form.get('contact')
        profile.cgpa = float(request.form.get('cgpa'))
        profile.department = request.form.get('department')
        
        # Handle resume upload
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename != '':
                if not file.filename.lower().endswith('.pdf'):
                    flash('Only PDF resumes are allowed.', 'danger')
                    return redirect(url_for('student.profile'))
                filename = secure_filename(f"resume_{current_user.id}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                profile.resume_path = filename
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('student.profile'))
        
    return render_template('student/profile.html', profile=profile)

@student_bp.route('/apply/<int:drive_id>')
@login_required
@student_required
def apply_for_drive(drive_id):
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    drive = PlacementDrive.query.get_or_404(drive_id)
    
    # Validation: Check if already applied
    existing_app = Application.query.filter_by(student_id=profile.id, drive_id=drive_id).first()
    if existing_app:
        flash('You have already applied for this placement drive.', 'warning')
        return redirect(url_for('student.dashboard'))
    
    # Validation: Check drive status and deadline
    if drive.status != 'Approved':
        flash('This drive is not accepting applications.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    if drive.deadline < datetime.utcnow():
        flash('The deadline for this drive has passed.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    # Validation: Check if resume is uploaded
    if not profile.resume_path:
        flash('You MUST upload a resume in your profile before applying.', 'danger')
        return redirect(url_for('student.profile'))
        
    # Validation: Hard CGPA check based on AI match layer
    cgpa_match = re.search(r'(\d\.?\d*)\s*(?:cgpa|gpa)', drive.eligibility_criteria.lower())
    if cgpa_match:
        required_cgpa = float(cgpa_match.group(1))
        if profile.cgpa < required_cgpa:
            flash(f'You are not eligible. Required CGPA is {required_cgpa}, your CGPA is {profile.cgpa}.', 'danger')
            return redirect(url_for('student.dashboard'))
    
    new_app = Application(student_id=profile.id, drive_id=drive_id)
    db.session.add(new_app)
    db.session.commit()
    
    flash(f'Application submitted for {drive.job_title}.', 'success')
    return redirect(url_for('student.history'))

@student_bp.route('/history')
@login_required
@student_required
def history():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    applications = Application.query.filter_by(student_id=profile.id).order_by(Application.application_date.desc()).all()
    return render_template('student/history.html', applications=applications)
