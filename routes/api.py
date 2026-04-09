from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, PlacementDrive, CompanyProfile, Application, StudentProfile

api_bp = Blueprint('api', __name__)

@api_bp.route('/companies', methods=['GET'])
def get_companies():
    companies = CompanyProfile.query.filter_by(approval_status='Approved').all()
    # Serialize companies to dict
    return jsonify([
        {
            'id': c.id,
            'name': c.name,
            'website': c.website,
            'description': c.description
        } for c in companies
    ])

@api_bp.route('/drives', methods=['GET'])
def get_drives():
    drives = PlacementDrive.query.filter_by(status='Approved').all()
    return jsonify([
        {
            'id': d.id,
            'company_name': d.company_profile.name,
            'job_title': d.job_title,
            'eligibility_criteria': d.eligibility_criteria,
            'deadline': d.deadline.strftime('%Y-%m-%dT%H:%M:%S') if d.deadline else None
        } for d in drives
    ])
