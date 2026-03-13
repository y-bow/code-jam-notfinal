from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.models import db, Internship
from app.middleware import school_scoped, role_minimum

internships_bp = Blueprint('internships', __name__, url_prefix='/internships')


@internships_bp.route('/')
@school_scoped
def index():
    """List all available internships."""
    internships = Internship.query.order_by(Internship.created_at.desc()).all()
    return render_template('internships/index.html', internships=internships)


@internships_bp.route('/new', methods=['GET', 'POST'])
@school_scoped
@role_minimum('dean')
def create():
    """Admin/Dean: create a new internship listing."""
    if request.method == 'POST':
        internship = Internship(
            company_name=request.form.get('company_name', '').strip(),
            role=request.form.get('role', '').strip(),
            location=request.form.get('location', '').strip(),
            duration=request.form.get('duration', '').strip(),
            stipend=request.form.get('stipend', '').strip() or None,
            description=request.form.get('description', '').strip() or None,
            required_skills=request.form.get('required_skills', '').strip() or None,
            application_link=request.form.get('application_link', '').strip() or None,
        )

        deadline_str = request.form.get('application_deadline', '').strip()
        if deadline_str:
            from datetime import datetime
            try:
                internship.application_deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid deadline format. Use YYYY-MM-DD.', 'error')
                return render_template('internships/form.html', internship=None)

        if not internship.company_name or not internship.role or not internship.location or not internship.duration:
            flash('Company name, role, location, and duration are required.', 'error')
            return render_template('internships/form.html', internship=None)

        db.session.add(internship)
        db.session.commit()
        flash(f'Internship at {internship.company_name} posted successfully!', 'success')
        return redirect(url_for('internships.index'))

    return render_template('internships/form.html', internship=None)


@internships_bp.route('/<int:internship_id>/edit', methods=['GET', 'POST'])
@school_scoped
@role_minimum('dean')
def edit(internship_id):
    """Admin/Dean: edit an existing internship listing."""
    internship = Internship.query.get_or_404(internship_id)

    if request.method == 'POST':
        internship.company_name = request.form.get('company_name', '').strip()
        internship.role = request.form.get('role', '').strip()
        internship.location = request.form.get('location', '').strip()
        internship.duration = request.form.get('duration', '').strip()
        internship.stipend = request.form.get('stipend', '').strip() or None
        internship.description = request.form.get('description', '').strip() or None
        internship.required_skills = request.form.get('required_skills', '').strip() or None
        internship.application_link = request.form.get('application_link', '').strip() or None

        deadline_str = request.form.get('application_deadline', '').strip()
        if deadline_str:
            from datetime import datetime
            try:
                internship.application_deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid deadline format. Use YYYY-MM-DD.', 'error')
                return render_template('internships/form.html', internship=internship)
        else:
            internship.application_deadline = None

        db.session.commit()
        flash('Internship updated successfully!', 'success')
        return redirect(url_for('internships.index'))

    return render_template('internships/form.html', internship=internship)


@internships_bp.route('/<int:internship_id>/delete', methods=['POST'])
@school_scoped
@role_minimum('dean')
def delete(internship_id):
    """Admin/Dean: delete an internship listing."""
    internship = Internship.query.get_or_404(internship_id)
    db.session.delete(internship)
    db.session.commit()
    flash('Internship listing removed.', 'success')
    return redirect(url_for('internships.index'))
