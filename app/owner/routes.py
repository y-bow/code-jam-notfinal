from flask import render_template, redirect, url_for, flash, request, session, abort
from . import owner_bp
from ..models import db, User, School, UniversityRegistration, PlatformAnnouncement, Section, Course, Student
from ..middleware import platform_owner_required
from ..models import bcrypt
import json
import plotly
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

@owner_bp.route('/dashboard')
@platform_owner_required
def dashboard():
    # 1. PLATFORM STATS STRIP
    total_universities = School.query.count()
    active_universities = School.query.filter_by(is_active=True).count()
    pending_approval = UniversityRegistration.query.filter_by(status='pending').count()
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_professors = User.query.filter(User.role.in_(['professor', 'assistant_professor'])).count()

    # 2. UNIVERSITY LIST TABLE (with filters and search)
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')

    query = School.query
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'suspended':
        query = query.filter_by(is_active=False)
    # 'pending' is handled in the registrations section

    if search_query:
        query = query.filter(School.name.ilike(f'%{search_query}%') | School.domain.ilike(f'%{search_query}%'))

    universities = query.all()

    # Data for the table
    uni_data = []
    for uni in universities:
        uni_data.append({
            'id': uni.id,
            'name': uni.name,
            'domain': uni.domain,
            'country': 'India', # Default or add to model if needed
            'students': User.query.filter_by(school_id=uni.id, role='student').count(),
            'professors': User.query.filter(User.school_id == uni.id, User.role.in_(['professor', 'assistant_professor'])).count(),
            'courses': Course.query.join(Section).filter(Section.school_id == uni.id).count(),
            'status': 'Active' if uni.is_active else 'Suspended',
            'joined_date': uni.created_at.strftime('%Y-%m-%d') if uni.created_at else 'N/A'
        })

    # 3. PENDING APPROVALS
    pending_registrations = UniversityRegistration.query.filter_by(status='pending').all()

    # 4. PLATFORM ANALYTICS (Plotly)
    # Line chart: new universities per month
    uni_growth = School.query.with_entities(School.created_at).all()
    df_uni = pd.DataFrame([u[0] for u in uni_growth if u[0]], columns=['date'])
    df_uni['month'] = df_uni['date'].dt.to_period('M').astype(str)
    uni_chart_data = df_uni.groupby('month').size().reset_index(name='count')
    fig_uni = px.line(uni_chart_data, x='month', y='count', title='New Universities per Month',
                     template='plotly_dark', color_discrete_sequence=['#a855f7']) # Purple accent
    uni_chart_json = json.dumps(fig_uni, cls=plotly.utils.PlotlyJSONEncoder)

    # Line chart: new users per month
    user_growth = User.query.with_entities(User.created_at).all()
    df_users = pd.DataFrame([u[0] for u in user_growth if u[0]], columns=['date'])
    df_users['month'] = df_users['date'].dt.to_period('M').astype(str)
    user_chart_data = df_users.groupby('month').size().reset_index(name='count')
    fig_users = px.line(user_chart_data, x='month', y='count', title='New Users per Month',
                       template='plotly_dark', color_discrete_sequence=['#eab308']) # Gold accent
    user_chart_json = json.dumps(fig_users, cls=plotly.utils.PlotlyJSONEncoder)

    # Bar chart: users per university
    uni_names = [u.name for u in School.query.all()]
    user_counts = [User.query.filter_by(school_id=u.id).count() for u in School.query.all()]
    fig_dist = px.bar(x=uni_names, y=user_counts, title='Users per University',
                     template='plotly_dark', color_discrete_sequence=['#a855f7'])
    dist_chart_json = json.dumps(fig_dist, cls=plotly.utils.PlotlyJSONEncoder)

    # Bar chart: active courses per university
    course_counts = [Course.query.join(Section).filter(Section.school_id == u.id).count() for u in School.query.all()]
    fig_courses = px.bar(x=uni_names, y=course_counts, title='Active Courses per University',
                        template='plotly_dark', color_discrete_sequence=['#eab308'])
    course_chart_json = json.dumps(fig_courses, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('dashboard.html',
                           total_universities=total_universities,
                           active_universities=active_universities,
                           pending_approval_count=pending_approval,
                           total_users=total_users,
                           total_students=total_students,
                           total_professors=total_professors,
                           universities=uni_data,
                           pending_registrations=pending_registrations,
                           uni_chart=uni_chart_json,
                           user_chart=user_chart_json,
                           dist_chart=dist_chart_json,
                           course_chart=course_chart_json)

@owner_bp.route('/university/<int:uni_id>')
@platform_owner_required
def university_detail(uni_id):
    uni = School.query.get_or_404(uni_id)
    admins = User.query.filter_by(school_id=uni.id, role='admin').all()
    student_count = User.query.filter_by(school_id=uni.id, role='student').count()
    professor_count = User.query.filter(User.school_id == uni.id, User.role.in_(['professor', 'assistant_professor'])).count()
    
    # Placeholder for recent activity and data upload history
    recent_activity = [] # Could be logs if implemented
    upload_history = []  # Assuming UploadLog or similar exists
    
    return render_template('university_detail.html',
                           uni=uni,
                           admins=admins,
                           student_count=student_count,
                           professor_count=professor_count,
                           recent_activity=recent_activity,
                           upload_history=upload_history)

@owner_bp.route('/approve-university/<int:reg_id>', methods=['POST'])
@platform_owner_required
def approve_university(reg_id):
    reg = UniversityRegistration.query.get_or_404(reg_id)
    reg.status = 'approved'
    
    # Create the School
    new_school = School(
        name=reg.university_name,
        domain=reg.domain,
        code=reg.university_name[:4].upper(), # Simplified code gen
        trust_level='verified',
        is_active=True
    )
    db.session.add(new_school)
    db.session.commit()
    
    # Create the Rep as Admin
    # Initial password should be sent in welcome email
    temp_pw = "HiveWelcome123!"
    rep_user = User(
        school_id=new_school.id,
        email=reg.rep_email,
        password_hash=bcrypt.generate_password_hash(temp_pw).decode('utf-8'),
        role='admin',
        name=reg.rep_name,
        must_change_password=True
    )
    db.session.add(rep_user)
    db.session.commit()
    
    flash(f"University '{reg.university_name}' approved. Welcome email sent to {reg.rep_email}.", "success")
    return redirect(url_for('owner.dashboard'))

@owner_bp.route('/reject-university/<int:reg_id>', methods=['POST'])
@platform_owner_required
def reject_university(reg_id):
    reason = request.form.get('reason')
    reg = UniversityRegistration.query.get_or_404(reg_id)
    reg.status = 'rejected'
    reg.rejection_reason = reason
    db.session.commit()
    
    flash(f"Registration for '{reg.university_name}' rejected.", "warning")
    return redirect(url_for('owner.dashboard'))

@owner_bp.route('/suspend-university/<int:uni_id>', methods=['POST'])
@platform_owner_required
def suspend_university(uni_id):
    uni = School.query.get_or_404(uni_id)
    uni.is_active = False
    db.session.commit()
    flash(f"University '{uni.name}' has been suspended.", "danger")
    return redirect(url_for('owner.dashboard'))

@owner_bp.route('/announcements', methods=['GET', 'POST'])
@platform_owner_required
def announcements():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        new_ann = PlatformAnnouncement(title=title, body=body)
        db.session.add(new_ann)
        db.session.commit()
        flash("System-wide announcement posted.", "success")
        return redirect(url_for('owner.announcements'))
    
    anns = PlatformAnnouncement.query.order_by(PlatformAnnouncement.posted_at.desc()).all()
    return render_template('announcements.html', announcements=anns)

@owner_bp.route('/settings', methods=['GET', 'POST'])
@platform_owner_required
def settings():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        
        if email:
            user.email = email
        if new_password:
            user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        db.session.commit()
        flash("Owner account settings updated.", "success")
        return redirect(url_for('owner.settings'))
        
    return render_template('settings.html', user=user)
