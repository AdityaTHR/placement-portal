from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, CompanyProfile, StudentProfile, PlacementDrive, Application

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_students': StudentProfile.query.count(),
        'total_companies': CompanyProfile.query.count(),
        'total_drives': PlacementDrive.query.count(),
        'total_applications': Application.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/companies')
@login_required
@admin_required
def manage_companies():
    query = request.args.get('search')
    if query:
        companies = CompanyProfile.query.filter(CompanyProfile.name.like(f'%{query}%')).all()
    else:
        companies = CompanyProfile.query.all()
    return render_template('admin/companies.html', companies=companies)

@admin_bp.route('/company/approve/<int:id>')
@login_required
@admin_required
def approve_company(id):
    profile = CompanyProfile.query.get_or_404(id)
    profile.approval_status = 'Approved'
    db.session.commit()
    flash(f'Company {profile.name} approved.', 'success')
    return redirect(url_for('admin.manage_companies'))

@admin_bp.route('/company/reject/<int:id>')
@login_required
@admin_required
def reject_company(id):
    profile = CompanyProfile.query.get_or_404(id)
    profile.approval_status = 'Rejected'
    db.session.commit()
    flash(f'Company {profile.name} rejected.', 'warning')
    return redirect(url_for('admin.manage_companies'))

@admin_bp.route('/drives')
@login_required
@admin_required
def manage_drives():
    drives = PlacementDrive.query.all()
    return render_template('admin/drives.html', drives=drives)

@admin_bp.route('/drive/approve/<int:id>')
@login_required
@admin_required
def approve_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'Approved'
    db.session.commit()
    flash('Placement drive approved.', 'success')
    return redirect(url_for('admin.manage_drives'))

@admin_bp.route('/drive/reject/<int:id>')
@login_required
@admin_required
def reject_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'Rejected'
    db.session.commit()
    flash('Placement drive rejected.', 'warning')
    return redirect(url_for('admin.manage_drives'))

@admin_bp.route('/students')
@login_required
@admin_required
def manage_students():
    query = request.args.get('search')
    if query:
        students = StudentProfile.query.filter(
            (StudentProfile.name.like(f'%{query}%')) | 
            (StudentProfile.user_id.like(f'%{query}%'))
        ).all()
    else:
        students = StudentProfile.query.all()
    return render_template('admin/students.html', students=students)

@admin_bp.route('/user/toggle-status/<int:user_id>')
@login_required
@admin_required
def toggle_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot deactivate admin.', 'danger')
        return redirect(request.referrer)
    
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated/blacklisted'
    flash(f'User {user.username} has been {status}.', 'info')
    return redirect(request.referrer)
