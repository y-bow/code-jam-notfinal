from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from ..models import db, Club, ExternalEvent
from ..permissions import (
    require_role, require_min_role, student_required, 
    dean_required, admin_required, school_scope
)
from datetime import datetime

clubs_bp = Blueprint('clubs', __name__, url_prefix='/clubs')

# =============================================================================
# STUDENT ROUTES
# =============================================================================

@clubs_bp.route('/')
@student_required
def index():
    clubs = school_scope(Club.query, Club).order_by(Club.name).all()
    events = school_scope(ExternalEvent.query, ExternalEvent).filter(
        ExternalEvent.date >= datetime.utcnow()
    ).order_by(ExternalEvent.date).limit(10 if g.current_user.role == 'admin' else 5).all()
    return render_template('clubs/student_clubs.html', clubs=clubs, events=events)


@clubs_bp.route('/<int:club_id>')
@student_required
def club_details(club_id):
    club = school_scope(Club.query, Club).filter_by(id=club_id).first_or_404()
    return render_template('clubs/club_details.html', club=club)


@clubs_bp.route('/events')
@student_required
def events():
    events = school_scope(ExternalEvent.query, ExternalEvent).filter(
        ExternalEvent.date >= datetime.utcnow()
    ).order_by(ExternalEvent.date).all()
    return render_template('clubs/student_events.html', events=events)


# =============================================================================
# ADMIN ROUTES
# =============================================================================

@clubs_bp.route('/admin', methods=['GET', 'POST'])
@dean_required
def admin_clubs():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description')
        contact_email = request.form.get('contact_email')
        
        club = Club(
            school_id=g.school_id,
            name=name, 
            category=category, 
            description=description, 
            contact_email=contact_email
        )
        db.session.add(club)
        db.session.commit()
        flash('Club created successfully.', 'success')
        return redirect(url_for('clubs.admin_clubs'))
        
    clubs = school_scope(Club.query, Club).order_by(Club.name).all()
    return render_template('clubs/admin_clubs.html', clubs=clubs)


@clubs_bp.route('/admin/edit/<int:club_id>', methods=['POST'])
@dean_required
def edit_club(club_id):
    club = school_scope(Club.query, Club).filter_by(id=club_id).first_or_404()

    club.name = request.form.get('name')
    club.category = request.form.get('category')
    club.description = request.form.get('description')
    club.contact_email = request.form.get('contact_email')
    
    db.session.commit()
    flash('Club updated successfully.', 'success')
    return redirect(url_for('clubs.admin_clubs'))

@clubs_bp.route('/admin/delete/<int:club_id>', methods=['POST'])
@dean_required
def delete_club(club_id):
    club = school_scope(Club.query, Club).filter_by(id=club_id).first_or_404()

    db.session.delete(club)
    db.session.commit()
    flash('Club deleted successfully.', 'success')
    return redirect(url_for('clubs.admin_clubs'))

@clubs_bp.route('/admin/events', methods=['GET', 'POST'])
@dean_required
def admin_events():
    if request.method == 'POST':
        title = request.form.get('title')
        hosting_college = request.form.get('hosting_college')
        date_str = request.form.get('date')
        location = request.form.get('location')
        description = request.form.get('description')
        registration_link = request.form.get('registration_link')
        
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M') if 'T' in date_str else datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('clubs.admin_events'))
        
        event = ExternalEvent(
            school_id=g.school_id,
            title=title, 
            hosting_college=hosting_college,
            date=event_date,
            location=location,
            description=description, 
            registration_link=registration_link
        )
        db.session.add(event)
        db.session.commit()
        flash('External event created successfully.', 'success')
        return redirect(url_for('clubs.admin_events'))
        
    events = school_scope(ExternalEvent.query, ExternalEvent).order_by(ExternalEvent.date.desc()).all()
    return render_template('clubs/admin_events.html', events=events)


@clubs_bp.route('/admin/events/edit/<int:event_id>', methods=['POST'])
@dean_required
def edit_event(event_id):
    event = school_scope(ExternalEvent.query, ExternalEvent).filter_by(id=event_id).first_or_404()

    event.title = request.form.get('title')
    event.hosting_college = request.form.get('hosting_college')
    
    date_str = request.form.get('date')
    if date_str:
        try:
            event.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M') if 'T' in date_str else datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
             pass # keep old date
            
    event.location = request.form.get('location')
    event.description = request.form.get('description')
    event.registration_link = request.form.get('registration_link')
    
    db.session.commit()
    flash('External event updated successfully.', 'success')
    return redirect(url_for('clubs.admin_events'))

@clubs_bp.route('/admin/events/delete/<int:event_id>', methods=['POST'])
@dean_required
def delete_event(event_id):
    event = school_scope(ExternalEvent.query, ExternalEvent).filter_by(id=event_id).first_or_404()

    db.session.delete(event)
    db.session.commit()
    flash('External event deleted successfully.', 'success')
    return redirect(url_for('clubs.admin_events'))
