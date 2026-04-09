from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from models import db, User, CompanyProfile, PlacementDrive, Application, StudentProfile
from datetime import datetime
import csv
from io import StringIO

company_bp = Blueprint('company', __name__)

def company_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'company':
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@company_bp.route('/dashboard')
@login_required
@company_required
def dashboard():
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    drives = PlacementDrive.query.filter_by(company_id=profile.id).all()
    
    # Calculate stats
    total_drives = len(drives)
    total_applicants = db.session.query(Application).join(PlacementDrive).filter(PlacementDrive.company_id == profile.id).count()
    
    return render_template('company/dashboard.html', profile=profile, drives=drives, total_drives=total_drives, total_applicants=total_applicants)

@company_bp.route('/drive/create', methods=['GET', 'POST'])
@login_required
@company_required
def create_drive():
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if profile.approval_status != 'Approved':
        flash('You can only create drives after admin approval.', 'warning')
        return redirect(url_for('company.dashboard'))
        
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        eligibility = request.form.get('eligibility')
        deadline_str = request.form.get('deadline')
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        
        new_drive = PlacementDrive(
            company_id=profile.id,
            job_title=job_title,
            job_description=job_description,
            eligibility_criteria=eligibility,
            deadline=deadline
        )
        db.session.add(new_drive)
        db.session.commit()
        flash('Placement drive created and sent for admin approval.', 'success')
        return redirect(url_for('company.dashboard'))
        
    return render_template('company/create_drive.html')

@company_bp.route('/drive/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@company_required
def edit_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    # Ensure company owns this drive
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if profile.approval_status != 'Approved':
        flash('You can only perform this action after admin approval.', 'warning')
        return redirect(url_for('company.dashboard'))
        
    if drive.company_id != profile.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('company.dashboard'))
        
    if request.method == 'POST':
        drive.job_title = request.form.get('job_title')
        drive.job_description = request.form.get('job_description')
        drive.eligibility_criteria = request.form.get('eligibility')
        drive.deadline = datetime.strptime(request.form.get('deadline'), '%Y-%m-%d')
        drive.status = 'Pending' # Reset to pending for re-approval
        db.session.commit()
        flash('Drive updated and sent for re-approval.', 'info')
        return redirect(url_for('company.dashboard'))
        
    return render_template('company/edit_drive.html', drive=drive)

@company_bp.route('/drive/delete/<int:id>')
@login_required
@company_required
def delete_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if profile.approval_status != 'Approved':
        flash('You can only perform this action after admin approval.', 'warning')
        return redirect(url_for('company.dashboard'))
        
    if drive.company_id != profile.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('company.dashboard'))
        
    db.session.delete(drive)
    db.session.commit()
    flash('Placement drive removed.', 'success')
    return redirect(url_for('company.dashboard'))

@company_bp.route('/drive/close/<int:id>')
@login_required
@company_required
def close_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if profile.approval_status != 'Approved':
        flash('You can only perform this action after admin approval.', 'warning')
        return redirect(url_for('company.dashboard'))
        
    if drive.company_id != profile.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('company.dashboard'))
        
    drive.status = 'Closed'
    db.session.commit()
    flash('Placement drive closed for applications.', 'info')
    return redirect(url_for('company.dashboard'))

@company_bp.route('/drive/applications/<int:drive_id>')
@login_required
@company_required
def view_applications(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if profile.approval_status != 'Approved':
        flash('You can only perform this action after admin approval.', 'warning')
        return redirect(url_for('company.dashboard'))
        
    if drive.company_id != profile.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('company.dashboard'))
        
    applications = Application.query.filter_by(drive_id=drive.id).all()
    return render_template('company/applications.html', drive=drive, applications=applications)

@company_bp.route('/application/update-status/<int:app_id>')
@login_required
@company_required
def update_app_status(app_id):
    app = Application.query.get_or_404(app_id)
    new_status = request.args.get('status')
    
    # Security check: Ensure company owns the drive for this application
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if profile.approval_status != 'Approved':
        flash('You can only perform this action after admin approval.', 'warning')
        return redirect(url_for('company.dashboard'))
        
    if app.placement_drive.company_id != profile.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('company.dashboard'))
        
    if new_status in ['Shortlisted', 'Selected', 'Rejected']:
        app.status = new_status
        db.session.commit()
        flash(f'Application status updated to {new_status}.', 'success')
    
    return redirect(url_for('company.view_applications', drive_id=app.drive_id))


@company_bp.route('/drive/export/<int:drive_id>')
@login_required
@company_required
def export_applications(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if profile.approval_status != 'Approved':
        flash('You can only perform this action after admin approval.', 'warning')
        return redirect(url_for('company.dashboard'))
        
    if drive.company_id != profile.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('company.dashboard'))
        
    applications = Application.query.filter_by(drive_id=drive.id).all()
    
    def generate():
        data = StringIO()
        writer = csv.writer(data)
        
        # Write header
        writer.writerow(('Student Name', 'CGPA', 'Department', 'Contact', 'Application Date', 'Status'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        
        # Write rows
        for app in applications:
            writer.writerow((
                app.student_profile.name,
                app.student_profile.cgpa,
                app.student_profile.department,
                app.student_profile.contact,
                app.application_date.strftime('%Y-%m-%d'),
                app.status
            ))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    response = Response(generate(), mimetype='text/csv')
    response.headers.set("Content-Disposition", f"attachment; filename=applications_{drive.id}.csv")
    return response
