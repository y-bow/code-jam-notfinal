from flask import Blueprint, render_template, request, redirect, url_for, g, flash, abort, jsonify
from datetime import datetime
from ..middleware import school_scoped, role_minimum
from ..models import db, Internship

internships_bp = Blueprint('internships', __name__, url_prefix='/internships')

@internships_bp.route('/', methods=['GET'])
@school_scoped
def index():
    query = Internship.query

    # Search by role or company name
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Internship.company_name.ilike(f'%{search}%'),
                Internship.role.ilike(f'%{search}%')
            )
        )

    # Filter by location
    location = request.args.get('location', '')
    if location:
        query = query.filter(Internship.location.ilike(f'%{location}%'))

    # Filter by duration
    duration = request.args.get('duration', '')
    if duration:
        query = query.filter(Internship.duration.ilike(f'%{duration}%'))

    internships = query.order_by(Internship.created_at.desc()).all()
    
    return render_template('internships.html', internships=internships, search=search, location=location, duration=duration)

@internships_bp.route('/api/<int:id>', methods=['GET'])
@school_scoped
def get_internship(id):
    internship = Internship.query.get_or_404(id)
    return jsonify({
        'id': internship.id,
        'company_name': internship.company_name,
        'role': internship.role,
        'location': internship.location,
        'duration': internship.duration,
        'stipend': internship.stipend,
        'application_deadline': internship.application_deadline.strftime('%Y-%m-%d') if internship.application_deadline else None,
        'description': internship.description,
        'required_skills': internship.required_skills,
        'application_link': internship.application_link
    })

@internships_bp.route('/add', methods=['POST'])
@school_scoped
@role_minimum('admin')
def add():
    company_name = request.form.get('company_name')
    role = request.form.get('role')
    location = request.form.get('location')
    duration = request.form.get('duration')
    stipend = request.form.get('stipend')
    deadline_str = request.form.get('application_deadline')
    description = request.form.get('description')
    required_skills = request.form.get('required_skills')
    application_link = request.form.get('application_link')

    deadline = None
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        except ValueError:
            pass

    new_internship = Internship(
        company_name=company_name,
        role=role,
        location=location,
        duration=duration,
        stipend=stipend,
        application_deadline=deadline,
        description=description,
        required_skills=required_skills,
        application_link=application_link
    )
    db.session.add(new_internship)
    db.session.commit()
    flash('Internship added successfully.', 'success')
    return redirect(url_for('internships.index'))

@internships_bp.route('/edit/<int:id>', methods=['POST'])
@school_scoped
@role_minimum('admin')
def edit(id):
    internship = Internship.query.get_or_404(id)
    
    internship.company_name = request.form.get('company_name', internship.company_name)
    internship.role = request.form.get('role', internship.role)
    internship.location = request.form.get('location', internship.location)
    internship.duration = request.form.get('duration', internship.duration)
    internship.stipend = request.form.get('stipend', internship.stipend)
    internship.description = request.form.get('description', internship.description)
    internship.required_skills = request.form.get('required_skills', internship.required_skills)
    internship.application_link = request.form.get('application_link', internship.application_link)

    deadline_str = request.form.get('application_deadline')
    if deadline_str:
        try:
            internship.application_deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        except ValueError:
            pass

    db.session.commit()
    flash('Internship updated successfully.', 'success')
    return redirect(url_for('internships.index'))

@internships_bp.route('/delete/<int:id>', methods=['POST'])
@school_scoped
@role_minimum('admin')
def delete(id):
    internship = Internship.query.get_or_404(id)
    db.session.delete(internship)
    db.session.commit()
    flash('Internship deleted successfully.', 'success')
    return redirect(url_for('internships.index'))
