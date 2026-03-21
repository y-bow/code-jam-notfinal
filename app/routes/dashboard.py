from flask import Blueprint, render_template, session, request, redirect, url_for, g, flash, abort, jsonify
from datetime import datetime
from ..middleware import school_scoped, role_minimum
from ..models import (
    db, User, Student, Course, Enrollment, Assignment, Submission,
    Section, CustomTask, Announcement, TimetableEntry,
    TeacherTodo, TeacherRating, Attendance, Grade, School,
    ProfessorAssistant, ClassRepNomination
)
import pandas as pd
import plotly.express as px
import plotly.utils
import json

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def format_time_12hr(time_str):
    """Normalize '10:40 AM' -> '10:40AM' and convert '14:30' -> '2:30PM'."""
    if not time_str: return ""
    time_str = time_str.strip()
    try:
        # Check if it's 24h format (HH:MM or HH:MM:SS)
        if ':' in time_str and 'AM' not in time_str.upper() and 'PM' not in time_str.upper():
            from datetime import datetime
            t = datetime.strptime(time_str[:5], "%H:%M")
            # Using lstrip('0') for cross-platform compatibility
            return t.strftime("%I:%M%p").lstrip('0')
    except:
        pass
    return time_str.replace(" ", "")


@dashboard_bp.route('/student')
@school_scoped
def student_dashboard():
    user = g.current_user
    today_classes = []
    
    current_day = datetime.now().weekday()
    if current_day <= 4:  # Monday to Friday
        if user.student_profile and user.student_profile.section_id:
            entries = TimetableEntry.query.filter_by(
                section_id=user.student_profile.section_id,
                day=current_day
            ).all()
            
            today_classes = [entry.to_dict() for entry in entries]
            # Sort by time
            today_classes.sort(key=lambda x: datetime.strptime(x['startTime'].replace(" ", "").upper(), '%I:%M%p').time() if 'AM' in x['startTime'].upper() or 'PM' in x['startTime'].upper() else x['startTime'])

    return render_template('dashboard/student_dashboard.html', today_classes=today_classes)


@dashboard_bp.route('/professor')
@school_scoped
@role_minimum('assistant_professor')
def professor_dashboard():
    user = g.current_user
    import plotly.utils
    import json

    # 1. Personalized Timetable (for courses taught by this professor OR assisted by them)
    if user.role == 'assistant_professor':
        assigned_courses = Course.query.join(ProfessorAssistant).filter(
            ProfessorAssistant.assistant_teacher_id == user.id,
            ProfessorAssistant.is_active == True
        ).all()
    else:
        assigned_courses = Course.query.filter_by(teacher_id=user.id).all()
    
    assigned_course_ids = [c.id for c in assigned_courses]
    
    # 2. Today's Classes
    current_day = datetime.now().weekday()
    today_classes = []
    if current_day <= 4:
        entries = (
            TimetableEntry.query
            .filter(TimetableEntry.course_id.in_(assigned_course_ids))
            .filter_by(day=current_day)
            .order_by(TimetableEntry.start_time)
            .all()
        )
        
        for entry in entries:
            # Add student count
            course = next((c for c in assigned_courses if c.name == entry.title), None)
            student_count = course.enrollments.count() if course else 0
            d = entry.to_dict()
            d['studentCount'] = student_count
            today_classes.append(d)
            
        today_classes.sort(key=lambda x: datetime.strptime(x['startTime'].replace(" ", "").upper(), '%I:%M%p').time() if 'AM' in x['startTime'].upper() or 'PM' in x['startTime'].upper() else x['startTime'])

    # 2. To-Do List
    tasks = TeacherTodo.query.filter_by(teacher_id=user.id).order_by(TeacherTodo.is_completed, TeacherTodo.created_at.desc()).all()

    # 3. Overall Stats
    total_students = db.session.query(db.func.count(db.distinct(Enrollment.student_id))).filter(Enrollment.course_id.in_(assigned_course_ids)).scalar() or 0
    managed_courses_count = len(assigned_courses)
    
    # 4. Rating Stats
    avg_rating = db.session.query(db.func.avg(TeacherRating.rating)).filter_by(teacher_id=user.id).scalar() or 0
    total_ratings = TeacherRating.query.filter_by(teacher_id=user.id).count()
    recent_reviews = TeacherRating.query.filter_by(teacher_id=user.id).order_by(TeacherRating.created_at.desc()).limit(5).all()

    # 5. Analytics Section (Plotly)
    graphs_json = {}

    # A. Bar chart: average grade per class
    grade_data = []
    for course in assigned_courses:
        avg_grade = db.session.query(db.func.avg(Grade.grade)).filter_by(course_id=course.id).scalar() or 0
        grade_data.append({'Course': course.code, 'Avg Grade': round(avg_grade, 2)})
    
    if grade_data:
        df_grades = pd.DataFrame(grade_data)
        fig_grades = px.bar(df_grades, x='Course', y='Avg Grade', title='Avg Grade per Class', template='plotly_dark')
        fig_grades.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        graphs_json['grades'] = json.dumps(fig_grades, cls=plotly.utils.PlotlyJSONEncoder)

    # B. Pie chart: attendance distribution % (present/absent/late)
    att_data = db.session.query(Attendance.status, db.func.count(Attendance.id)).filter(Attendance.course_id.in_(assigned_course_ids)).group_by(Attendance.status).all()
    if att_data:
        df_att = pd.DataFrame(att_data, columns=['Status', 'Count'])
        fig_att = px.pie(df_att, values='Count', names='Status', title='Attendance Distribution', template='plotly_dark')
        fig_att.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        graphs_json['attendance'] = json.dumps(fig_att, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('dashboard/professor_dashboard.html', 
                           today_classes=today_classes, 
                           tasks=tasks, 
                           stats={
                               'students': total_students, 
                               'courses': managed_courses_count,
                               'rating': round(float(avg_rating), 1),
                               'rating_count': total_ratings
                           },
                            reviews=recent_reviews,
                            graphs=graphs_json)


@dashboard_bp.route('/admin')
@school_scoped
@role_minimum('admin')
def admin_dashboard():
    """Global Admin Dashboard: system-wide overview."""
    total_schools = School.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_professors = User.query.filter_by(role='professor').count()
    total_courses = Course.query.count()

    schools = School.query.all()
    school_data = []
    for s in schools:
        s_students = User.query.filter_by(school_id=s.id, role='student').count()
        s_professors = User.query.filter_by(school_id=s.id, role='professor').count()
        s_courses = Course.query.join(Section).filter(Section.school_id == s.id).count()
        
        # Simple calculations for demo/analytics
        avg_cgpa = db.session.query(db.func.avg(Student.cgpa)).join(User).filter(User.school_id == s.id).scalar() or 0
        
        school_data.append({
            'name': s.name,
            'students': s_students,
            'professors': s_professors,
            'courses': s_courses,
            'avg_cgpa': round(float(avg_cgpa), 2),
            'avg_attendance': "85%", # Placeholder or derived
            'status': 'active' if s.is_active else 'inactive'
        })

    recent_activity = [] # Placeholder for audit logs if implemented
    
    return render_template('dashboard/admin_dashboard_global.html', 
                           stats={
                               'schools': total_schools,
                               'students': total_students,
                               'professors': total_professors,
                               'courses': total_courses,
                               'sections': Section.query.count()
                           },
                           school_data=school_data,
                           schools=schools,
                           announcements=Announcement.query.filter_by(school_id=None).order_by(Announcement.posted_at.desc()).limit(5).all())


@dashboard_bp.route('/admin/timetable', methods=['GET'])
@school_scoped
@role_minimum('admin')
def admin_timetable():
    """Editable timetable grid for admins."""
    if g.current_user.role == 'admin':
        sections = Section.query.all()
    else:
        sections = Section.query.filter_by(school_id=g.school_id).all()
    selected_section_id = request.args.get('section_id', type=int)
    
    # Default to first section if none selected
    if not selected_section_id and sections:
        selected_section_id = sections[0].id
    
    # Use a list of lists for days (0-4) - safer for Jinja iteration
    timetable = [[] for _ in range(5)]
    selected_section = None
    
    if selected_section_id:
        selected_section = Section.query.get(selected_section_id)
        if selected_section and (g.current_user.role == 'admin' or selected_section.school_id == g.school_id):
            for day_idx in range(5):
                entries = TimetableEntry.query.filter_by(
                    section_id=selected_section_id, 
                    day=day_idx
                ).order_by(TimetableEntry.start_time).all()
                
                timetable[day_idx] = [e.to_dict() for e in entries]
                # Map IDs for modal
                for i, d in enumerate(timetable[day_idx]):
                    d['id'] = entries[i].id
            
            print(f"DEBUG: Loaded {sum(len(d) for d in timetable)} entries for section {selected_section.name}")
        else:
            print(f"DEBUG: Section {selected_section_id} not found or school mismatch (G.School: {g.school_id})")

    return render_template('dashboard/admin_timetable.html', 
                           sections=sections, 
                           selected_section=selected_section,
                           timetable=timetable)


@dashboard_bp.route('/admin/timetable/debug')
@school_scoped
@role_minimum('admin')
def timetable_debug():
    """Diagnostic route to confirm data exists in DB."""
    query = TimetableEntry.query.join(Section)
    if g.current_user.role != 'admin':
        query = query.filter(Section.school_id == g.school_id)
    rows = query.all()
    return jsonify([r.to_dict() for r in rows])


@dashboard_bp.route('/admin/timetable/update', methods=['POST'])
@school_scoped
@role_minimum('admin')
def admin_timetable_update():
    """Update a timetable entry and auto-generate specialized announcements."""
    entry_id = request.form.get('entry_id', type=int)
    new_subject = request.form.get('subject')
    new_professor = request.form.get('professor')
    new_period = request.form.get('period')
    new_room = request.form.get('room')
    new_start = format_time_12hr(request.form.get('start_time'))
    new_end = format_time_12hr(request.form.get('end_time'))
    
    entry = TimetableEntry.query.get_or_404(entry_id)
    if g.current_user.role != 'admin' and entry.section.school_id != g.school_id:
        abort(403)
        
    old_subject = entry.title
    old_room = entry.room
    old_professor = entry.teacher
    old_start = entry.start_time
    old_end = entry.end_time
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    day_name = days[entry.day] if 0 <= entry.day < 5 else "Unspecified Day"
    
    # Update times first
    if new_start: entry.start_time = new_start
    if new_end: entry.end_time = new_end

    # 1. Subject Change
    if new_subject and new_subject != old_subject:
        entry.title = new_subject
        body = f"📚 Timetable Update ({entry.section.name}): {day_name} {entry.start_time}–{entry.end_time} — '{old_subject}' has been changed to '{new_subject}'."
        db.session.add(Announcement(school_id=g.school_id, section_id=entry.section_id, teacher_id=g.current_user.id, category='timetable', title="📚 Timetable Update", body=body))
    
    # 2. Room Change
    if new_room and new_room != old_room:
        entry.room = new_room
        body = f"🚪 Room Change ({entry.section.name}): {entry.title} on {day_name} {entry.start_time}–{entry.end_time} has moved from {old_room} to {new_room}."
        db.session.add(Announcement(school_id=g.school_id, section_id=entry.section_id, teacher_id=g.current_user.id, category='timetable', title="🚪 Room Change", body=body))

    # 3. Professor Change
    if new_professor and new_professor != old_professor:
        entry.teacher = new_professor
        body = f"👨‍🏫 Professor Change ({entry.section.name}): {entry.title} on {day_name} will now be taught by {new_professor} instead of {old_professor}."
        db.session.add(Announcement(school_id=g.school_id, section_id=entry.section_id, teacher_id=g.current_user.id, category='timetable', title="👨‍🏫 Professor Change", body=body))

    entry.period = new_period
    db.session.commit()
    
    flash(f"Timetable updated. Announcement sent to Section {entry.section.name} students.", "success")
    return redirect(url_for('dashboard.admin_timetable', section_id=entry.section_id))


@dashboard_bp.route('/admin/timetable/add', methods=['POST'])
@school_scoped
@role_minimum('admin')
def admin_timetable_add():
    """Add a new timetable slot and notify students."""
    section_id = request.form.get('section_id', type=int)
    day = request.form.get('day', type=int)
    start_time = format_time_12hr(request.form.get('start_time'))
    end_time = format_time_12hr(request.form.get('end_time'))
    subject = request.form.get('subject')
    professor = request.form.get('professor')
    room = request.form.get('room')
    period = request.form.get('period')
    color = request.form.get('color', 'var(--primary-color)')

    section = Section.query.get_or_404(section_id)
    if section.school_id != g.school_id:
        abort(403)

    new_entry = TimetableEntry(
        section_id=section_id,
        day=day,
        start_time=start_time,
        end_time=end_time,
        title=subject,
        teacher=professor,
        room=room,
        period=period,
        color=color,
        status='active'
    )
    db.session.add(new_entry)
    db.session.commit()

    # Auto-Announcement
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    day_name = days[day] if 0 <= day < 5 else "Unspecified Day"
    
    announcement = Announcement(
        school_id=g.school_id,
        section_id=section_id,
        teacher_id=g.current_user.id,
        category='timetable',
        title="📌 New Class Added",
        body=f"📌 New Class ({section.name}): {subject} added on {day_name} from {start_time} to {end_time} in {room} with {professor}.",
        posted_at=datetime.utcnow()
    )
    db.session.add(announcement)
    db.session.commit()

    flash(f"Timetable updated. Announcement sent to Section {section.name} students.", "success")
    return redirect(url_for('dashboard.admin_timetable', section_id=section_id))


@dashboard_bp.route('/admin/timetable/cancel', methods=['POST'])
@school_scoped
@role_minimum('admin')
def admin_timetable_cancel():
    """Cancel a timetable slot (soft delete)."""
    entry_id = request.form.get('entry_id', type=int)
    entry = TimetableEntry.query.get_or_404(entry_id)
    
    if entry.section.school_id != g.school_id:
        abort(403)

    entry.status = 'cancelled'
    db.session.commit()

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    day_name = days[entry.day] if 0 <= entry.day < 5 else "Unspecified Day"

    announcement = Announcement(
        school_id=g.school_id,
        section_id=entry.section_id,
        teacher_id=g.current_user.id,
        category='timetable',
        title="❌ Class Cancelled",
        body=f"❌ Class Cancelled (Section {entry.section.name}): {entry.title} on {day_name} ({entry.start_time}–{entry.end_time}) has been cancelled.",
        posted_at=datetime.utcnow()
    )
    db.session.add(announcement)
    db.session.commit()

    flash(f"Class cancelled. Announcement sent to Section {entry.section.name} students.", "success")
    return redirect(url_for('dashboard.admin_timetable', section_id=entry.section_id))


@dashboard_bp.route('/admin/timetable/restore', methods=['POST'])
@school_scoped
@role_minimum('admin')
def admin_timetable_restore():
    """Un-cancel a timetable slot."""
    entry_id = request.form.get('entry_id', type=int)
    entry = TimetableEntry.query.get_or_404(entry_id)
    
    if entry.section.school_id != g.school_id:
        abort(403)

    entry.status = 'active'
    db.session.commit()

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    day_name = days[entry.day] if 0 <= entry.day < 5 else "Unspecified Day"

    announcement = Announcement(
        school_id=g.school_id,
        section_id=entry.section_id,
        teacher_id=g.current_user.id,
        category='timetable',
        title="✅ Class Restored",
        body=f"✅ Class Restored (Section {entry.section.name}): {entry.title} on {day_name} ({entry.start_time}–{entry.end_time}) is back on schedule.",
        posted_at=datetime.utcnow()
    )
    db.session.add(announcement)
    db.session.commit()

    flash(f"Class restored. Announcement sent to Section {entry.section.name} students.", "success")
    return redirect(url_for('dashboard.admin_timetable', section_id=entry.section_id))


@dashboard_bp.route('/admin/timetable/delete', methods=['POST'])
@school_scoped
@role_minimum('admin')
def admin_timetable_delete():
    """Hard delete a timetable slot."""
    entry_id = request.form.get('entry_id', type=int)
    entry = TimetableEntry.query.get_or_404(entry_id)
    
    if entry.section.school_id != g.school_id:
        abort(403)

    section_id = entry.section_id
    section_name = entry.section.name
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    day_name = days[entry.day] if 0 <= entry.day < 5 else "Unspecified Day"
    info = f"{entry.title} on {day_name} ({entry.start_time}–{entry.end_time})"

    db.session.delete(entry)
    db.session.commit()

    announcement = Announcement(
        school_id=g.school_id,
        section_id=section_id,
        teacher_id=g.current_user.id,
        category='timetable',
        title="🗑️ Class Removed",
        body=f"🗑️ Class Removed (Section {section_name}): {info} has been permanently removed from the timetable.",
        posted_at=datetime.utcnow()
    )
    db.session.add(announcement)
    db.session.commit()

    flash(f"Class permanently deleted. Announcement sent to Section {section_name} students.", "success")
    return redirect(url_for('dashboard.admin_timetable', section_id=section_id))


@dashboard_bp.route('/timetable', methods=['GET', 'POST'])
@school_scoped
def timetable():
    user = g.current_user
    
    timetable_data = {}
    my_section_id = None
    if user.role == 'student':
        profile = user.student_profile
        if profile and profile.section_id:
            my_section_id = profile.section_id
    
    # If student, show their section's timetable
    if my_section_id:
        # Mon=0, Sat=5
        for day_idx in range(6):
            # Show all classes for student, so they see cancelled ones with strikethrough
            entries = TimetableEntry.query.filter_by(
                section_id=my_section_id, 
                day=day_idx
            ).order_by(TimetableEntry.start_time).all()
            
            timetable_data[day_idx] = [
                {
                    'startTime': e.start_time,
                    'endTime': e.end_time,
                    'title': e.title,
                    'room': e.room,
                    'color': e.color or 'var(--primary-color)',
                    'status': e.status
                } for e in entries
            ]
        
        # Sort by actual time correctly
        for day in timetable_data:
            timetable_data[day].sort(key=lambda x: datetime.strptime(x['startTime'].replace(" ", "").upper(), '%I:%M%p').time() if 'AM' in x['startTime'].upper() or 'PM' in x['startTime'].upper() else x['startTime'])
            
    # Calculate current day of week (0=Monday, 6=Sunday)
    current_day = datetime.now().weekday()
    # If it's weekend, we set it to something outside 0-4
    if current_day > 4:
        current_day = -1

    if user.role in ['professor', 'assistant_professor']:
        entries = db.session.query(TimetableEntry, Course, Section)\
            .join(Course, TimetableEntry.course_id == Course.id)\
            .join(Section, TimetableEntry.section_id == Section.id)\
            .filter(Course.teacher_id == user.id)\
            .order_by(TimetableEntry.day, TimetableEntry.start_time)\
            .all()
            
        timetable_data = {i: [] for i in range(5)}
        sections_taught = set()
        teaching_minutes = 0
        total_classes = len(entries)
        
        for e, c, s in entries:
            try:
                st = datetime.strptime(e.start_time.replace(" ", "").upper(), '%I:%M%p')
                et = datetime.strptime(e.end_time.replace(" ", "").upper(), '%I:%M%p')
                duration = int((et - st).total_seconds() / 60)
                teaching_minutes += duration
            except Exception:
                duration = 0

            if 0 <= e.day <= 4:
                timetable_data[e.day].append({
                    'course_name': c.name,
                    'course_code': c.code,
                    'section': s.code,
                    'start_time': e.start_time,
                    'end_time': e.end_time,
                    'room': e.room,
                    'status': e.status,
                    'color': e.color or 'var(--primary-color)',
                    'duration': duration
                })
            sections_taught.add(s.code)

        for day in timetable_data:
            timetable_data[day].sort(key=lambda x: datetime.strptime(x['start_time'].replace(" ", "").upper(), '%I:%M%p').time() if 'AM' in x['start_time'].upper() or 'PM' in x['start_time'].upper() else x['start_time'])
            
        hours = teaching_minutes // 60
        mins = teaching_minutes % 60
        teaching_hours_str = f"{hours}h {mins}m"
        
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        return render_template('dashboard/timetable_teacher.html',
                               timetable_data=timetable_data,
                               current_day=current_day,
                               total_classes=total_classes,
                               teaching_hours=teaching_hours_str,
                               sections_taught=sorted(list(sections_taught)))

    elif user.role in ['student', 'class_rep']:
        # Free Slots Logic Integration
        sections = []
        my_section = None
        selected_section = None
        free_slots_by_day = None

        if my_section_id:
            my_section = Section.query.get(my_section_id)
            # Load all sections from all schools
            sections = Section.query.join(School).order_by(School.name, Section.name).all()
            
            if request.method == 'POST':
                selected_section_id = request.form.get('compare_section_id', type=int)
                if selected_section_id:
                    selected_section = Section.query.get(selected_section_id)
                    if selected_section:
                        free_slots_by_day = get_common_free_slots(my_section_id, selected_section_id)

        return render_template('dashboard/timetable.html', 
                             timetable_data=timetable_data, 
                             current_day=current_day,
                             sections=sections,
                             my_section=my_section,
                             selected_section=selected_section,
                             free_slots_by_day=free_slots_by_day)

    else:
        # All other roles (dean, admin, etc.) get a system wide view
        all_entries = db.session.query(TimetableEntry, Section)\
            .join(Section, TimetableEntry.section_id == Section.id)\
            .order_by(TimetableEntry.day, TimetableEntry.start_time).all()
        return render_template('dashboard/timetable_system.html', all_entries=all_entries)



def get_common_free_slots(section_a_id, section_b_id):
    """
    Finds continuous common free slots across the 9:00 AM to 5:15 PM day.
    Merges busy intervals for both sections to find gaps >= 15 mins.
    """
    entries_a = TimetableEntry.query.filter_by(section_id=section_a_id).all()
    entries_b = TimetableEntry.query.filter_by(section_id=section_b_id).all()
    
    # Fetch courses for section_b to map course name to teacher name
    section_b_courses = Course.query.filter_by(section_id=section_b_id).all()
    course_teacher_map = {}
    for c in section_b_courses:
        if c.teacher:
            course_teacher_map[c.name] = c.teacher.name

    def to_minutes(t_str):
        t = datetime.strptime(t_str.strip().replace(" ", "").upper(), "%I:%M%p")
        return t.hour * 60 + t.minute

    def to_time_str(mins):
        h = mins // 60
        m = mins % 60
        is_pm = h >= 12
        display_h = h if h <= 12 else h - 12
        if display_h == 0: display_h = 12
        ampm = "PM" if is_pm else "AM"
        return f"{display_h}:{m:02d} {ampm}"
        
    DAYS_MAP = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday'}
    DAY_START = 9 * 60       # 09:00 AM
    DAY_END = 17 * 60 + 15   # 05:15 PM
    
    free_slots_by_day = []
    
    for day_idx in range(5):
        busy_intervals = []
        b_day_entries = []
        for e in entries_a + entries_b:
            if e.day == day_idx:
                try:
                    start_m = to_minutes(e.start_time)
                    end_m = to_minutes(e.end_time)
                    busy_intervals.append((start_m, end_m))
                    if e.section_id == section_b_id:
                        b_day_entries.append((start_m, e.title))
                except Exception:
                    pass
                    
        # Process classes for section_b on this day
        b_day_entries.sort(key=lambda x: x[0])
        day_classes = []
        seen_titles = set()
        for _, title in b_day_entries:
            if title not in seen_titles:
                teacher_name = course_teacher_map.get(title, "Unknown")
                day_classes.append({'title': title, 'teacher_name': teacher_name})
                seen_titles.add(title)

        # Merge overlapping intervals
        busy_intervals.sort(key=lambda x: x[0])
        merged = []
        for interval in busy_intervals:
            if not merged:
                merged.append([interval[0], interval[1]])
            else:
                prev = merged[-1]
                if interval[0] <= prev[1]:
                    prev[1] = max(prev[1], interval[1])
                else:
                    merged.append([interval[0], interval[1]])
                    
        # Find free gaps within DAY_START and DAY_END
        gaps = []
        current_time = DAY_START
        for start, end in merged:
            clp_ctime = max(current_time, DAY_START)
            clp_start = min(start, DAY_END)
            
            if clp_start > clp_ctime:
                gap_len = clp_start - clp_ctime
                if gap_len >= 15:
                    gaps.append((clp_ctime, clp_start, gap_len))
            
            current_time = max(current_time, end)
            
        # Check gap after last class until DAY_END
        clp_ctime = max(current_time, DAY_START)
        if clp_ctime < DAY_END:
            gap_len = DAY_END - clp_ctime
            if gap_len >= 15:
                gaps.append((clp_ctime, DAY_END, gap_len))
                
        if not gaps:
            free_slots_by_day.append({
                'day_name': DAYS_MAP[day_idx],
                'slots': [],
                'msg': "No common free time",
                'has_free': False,
                'classes': day_classes
            })
        else:
            if len(gaps) == 1 and gaps[0][0] == DAY_START and gaps[0][1] == DAY_END:
                msg = "All day free"
                has_free = True
                slots_formatted = []
            else:
                msg = ""
                has_free = True
                slots_formatted = [
                    {'text': f"{to_time_str(g[0])} – {to_time_str(g[1])}", 'duration': g[2]} 
                    for g in gaps
                ]
                
            free_slots_by_day.append({
                'day_name': DAYS_MAP[day_idx],
                'slots': slots_formatted,
                'msg': msg,
                'has_free': has_free,
                'classes': day_classes
            })
            
    return free_slots_by_day


@dashboard_bp.route('/tasks', methods=['GET', 'POST'])
@school_scoped
def tasks():
    user = g.current_user
    if request.method == 'POST':
        title = request.form.get('title')
        due_date_str = request.form.get('due_date')
        from datetime import datetime
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        new_task = CustomTask(user_id=user.id, title=title, due_date=due_date)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('dashboard.tasks'))

    custom_tasks = (
        CustomTask.query
        .filter_by(user_id=user.id)
        .order_by(CustomTask.is_completed, CustomTask.due_date.asc())
        .all()
    )
    custom_tasks.sort(key=lambda x: (x.is_completed, x.due_date is None, x.due_date))
    return render_template('dashboard/tasks.html', custom_tasks=custom_tasks)


@dashboard_bp.route('/tasks/toggle/<int:task_id>', methods=['POST'])
@school_scoped
def toggle_task(task_id):
    task = CustomTask.query.get_or_404(task_id)
    if task.user_id == g.current_user.id:
        task.is_completed = not task.is_completed
        db.session.commit()
    return redirect(url_for('dashboard.tasks'))


@dashboard_bp.route('/tasks/delete/<int:task_id>', methods=['POST'])
@school_scoped
def delete_task(task_id):
    task = CustomTask.query.get_or_404(task_id)
    if task.user_id == g.current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('dashboard.tasks'))


@dashboard_bp.route('/teacher/tasks/add', methods=['POST'])
@school_scoped
@role_minimum('assistant_professor')
def add_teacher_task():
    title = request.form.get('title')
    if title:
        new_task = TeacherTodo(teacher_id=g.current_user.id, title=title)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('dashboard.teacher_dashboard'))


@dashboard_bp.route('/teacher/tasks/toggle/<int:task_id>', methods=['POST'])
@school_scoped
@role_minimum('assistant_professor')
def toggle_teacher_task(task_id):
    task = TeacherTodo.query.get_or_404(task_id)
    if task.teacher_id == g.current_user.id:
        task.is_completed = not task.is_completed
        db.session.commit()
    return redirect(url_for('dashboard.teacher_dashboard'))


@dashboard_bp.route('/teacher/tasks/delete/<int:task_id>', methods=['POST'])
@school_scoped
@role_minimum('assistant_professor')
def delete_teacher_task(task_id):
    task = TeacherTodo.query.get_or_404(task_id)
    if task.teacher_id == g.current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('dashboard.teacher_dashboard'))


@dashboard_bp.route('/teacher/update_meet', methods=['POST'])
@school_scoped
@role_minimum('professor')
def update_meet_link():
    course_id = request.form.get('course_id')
    meet_link = request.form.get('meet_link')
    course = Course.query.get_or_404(course_id)
    if course.teacher_id == g.current_user.id:
        course.meet_link = meet_link
        db.session.commit()
        flash('Meeting link updated successfully.', 'success')
    return redirect(url_for('dashboard.teacher_dashboard'))


@dashboard_bp.route('/grades')
@school_scoped
def grades():
    return render_template('dashboard/grades.html')


@dashboard_bp.route('/announcements')
@school_scoped
def announcements():
    """School-wide and section-targeted announcements feed."""
    user = g.current_user
    my_section_id = None
    if user.role == 'student':
        profile = user.student_profile
        if profile:
            my_section_id = profile.section_id

    # Filter: school-wide (section_id IS NULL) OR targeted to user's section
    query = Announcement.query.filter(Announcement.school_id == g.school_id)
    if my_section_id:
        query = query.filter(
            (Announcement.section_id == None) | 
            (Announcement.section_id == my_section_id)
        )
        
    announcements_list = query.order_by(Announcement.posted_at.desc()).all()
    return render_template('dashboard/announcements.html', announcements=announcements_list)



# Legacy messages route removed. Use the 'messages' blueprint instead.


# =============================================================================
# SCHOOL-SCOPED DATA QUERIES (example endpoints)
# =============================================================================

@dashboard_bp.route('/my-courses')
@school_scoped
def my_courses():
    """Fetch courses scoped by role and school."""
    user = g.current_user

    if user.role in ('student', 'class_rep'):
        courses = (
            Course.query
            .join(Enrollment, Enrollment.course_id == Course.id)
            .join(Section, Course.section_id == Section.id)
            .filter(
                Enrollment.student_id == user.id,
                Section.school_id == g.school_id
            )
            .all()
        )
    elif user.role == 'professor':
        courses = (
            Course.query
            .join(Section)
            .filter(
                Course.teacher_id == user.id,
                Section.school_id == g.school_id
            )
            .all()
        )
    elif user.role == 'assistant_professor':
        # Courses where they are an active PA
        courses = (
            Course.query
            .join(ProfessorAssistant, ProfessorAssistant.course_id == Course.id)
            .filter(
                ProfessorAssistant.assistant_teacher_id == user.id,
                ProfessorAssistant.is_active == True
            )
            .all()
        )
    elif user.role in ('dean', 'professor'):
        courses = (
            Course.query
            .join(Section)
            .filter(Section.school_id == g.school_id)
            .all()
        )
    else:
        courses = []

    return render_template('dashboard/courses.html', courses=courses)


@dashboard_bp.route('/analytics')
@school_scoped
@role_minimum('dean')
def school_analytics():
    """Dean-only: analytics scoped to their school."""
    total_students = User.query.filter_by(school_id=g.school_id, role='student').count()
    total_professors = User.query.filter_by(school_id=g.school_id, role='professor').count()
    total_sections = Section.query.filter_by(school_id=g.school_id).count()
    total_courses = (
        Course.query
        .join(Section)
        .filter(Section.school_id == g.school_id)
        .count()
    )

    # Calculate average attendance (simplified: avg of all student attendance records)
    avg_attendance_raw = db.session.query(db.func.avg(Attendance.status == 'present')).filter(
        User.school_id == g.school_id, User.role == 'student'
    ).join(User, Attendance.student_id == User.id).scalar()
    avg_attendance = round(float(avg_attendance_raw) * 100, 1) if avg_attendance_raw is not None else 0.0

    # Calculate average CGPA
    from ..models import Student
    avg_cgpa_raw = db.session.query(db.func.avg(Student.cgpa)).join(User).filter(
        User.school_id == g.school_id
    ).scalar()
    avg_cgpa = round(float(avg_cgpa_raw), 2) if avg_cgpa_raw is not None else 0.0

    # At-risk students (attendance < 75%)
    at_risk_count = 0
    # This logic depends on how attendance is stored. 
    # For now, let's just use a placeholder or basic query.
    
    return render_template('dashboard/analytics.html',
                           total_students=total_students,
                           total_teachers=total_teachers,
                           total_sections=total_sections,
                           total_courses=total_courses,
                           avg_attendance=avg_attendance,
                           avg_cgpa=avg_cgpa)

@dashboard_bp.route('/dean/ratings')
@school_scoped
@role_minimum('dean')
def dean_ratings():
    """Dean-only: view teacher performance ratings."""
    professors = User.query.filter_by(school_id=g.school_id, role='professor').all()
    
    teacher_stats = []
    for t in teachers:
        avg_rating = db.session.query(db.func.avg(TeacherRating.rating)).filter_by(teacher_id=t.id).scalar() or 0
        total_ratings = TeacherRating.query.filter_by(teacher_id=t.id).count()
        teacher_stats.append({
            'id': t.id,
            'name': t.name,
            'avg_rating': round(float(avg_rating), 1) if avg_rating else 0.0,
            'total_ratings': total_ratings,
            'recent_reviews': TeacherRating.query.filter_by(teacher_id=t.id).order_by(TeacherRating.created_at.desc()).limit(3).all()
        })
        
    return render_template('dashboard/dean_ratings.html', teacher_stats=teacher_stats)

@dashboard_bp.route('/dean/nominations')
@school_scoped
@role_minimum('dean')
def dean_nominations():
    """Dean-only: approve or reject class rep nominations."""
    nominations = ClassRepNomination.query.join(Section).filter(
        Section.school_id == g.school_id, 
        ClassRepNomination.status == 'pending'
    ).all()
    return render_template('dashboard/dean_nominations.html', nominations=nominations)

@dashboard_bp.route('/dean/nominations/<int:nom_id>/<action>', methods=['POST'])
@school_scoped
@role_minimum('dean')
def handle_nomination(nom_id, action):
    nom = ClassRepNomination.query.get_or_404(nom_id)
    # Security check: nomination belongs to dean's school
    if nom.section.school_id != g.school_id:
        abort(403)
    
    if action == 'approve':
        nom.status = 'approved'
        nom.approved_by = g.current_user.id
        nom.decided_at = datetime.utcnow()
        # Promote student to class_rep role
        student = User.query.get(nom.student_id)
        student.role = 'class_rep'
        flash(f'Class Rep nomination for {student.name} approved.', 'success')
    elif action == 'reject':
        nom.status = 'rejected'
        nom.approved_by = g.current_user.id
        nom.decided_at = datetime.utcnow()
        flash('Class Rep nomination rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('dashboard.dean_nominations'))

@dashboard_bp.route('/timetable/manage', methods=['GET', 'POST'])
@school_scoped
@role_minimum('professor')
def manage_timetable():
    """Manage timetable entries for the school."""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            new_entry = TimetableEntry(
                section_id=request.form.get('section_id'),
                day=int(request.form.get('day')),
                start_time=request.form.get('start_time'),
                end_time=request.form.get('end_time'),
                title=request.form.get('title'),
                room=request.form.get('room'),
                color=request.form.get('color', 'var(--primary-color)')
            )
            # Verify section belongs to school
            section = Section.query.get(new_entry.section_id)
            if section and section.school_id == g.school_id:
                db.session.add(new_entry)
                db.session.commit()
                flash('Timetable entry added!', 'success')
            else:
                flash('Invalid section.', 'danger')
        elif action == 'delete':
            entry_id = request.form.get('entry_id')
            entry = TimetableEntry.query.get(entry_id)
            if entry and entry.section.school_id == g.school_id:
                db.session.delete(entry)
                db.session.commit()
                flash('Entry deleted.', 'info')

        return redirect(url_for('dashboard.manage_timetable'))

    sections = Section.query.filter_by(school_id=g.school_id).all()
    entries = (
        TimetableEntry.query
        .join(Section)
        .filter(Section.school_id == g.school_id)
        .order_by(Section.code, TimetableEntry.day, TimetableEntry.start_time)
        .all()
    )
    return render_template('dashboard/manage_timetable.html', sections=sections, entries=entries)


# --- Schools Management ---
@dashboard_bp.route('/admin/schools')
@school_scoped
@role_minimum('admin')
def admin_schools():
    if g.current_user.role != 'admin': # Only Global Admin can see all schools
        abort(403)
    schools = School.query.all()
    return render_template('dashboard/admin_schools.html', schools=schools)

@dashboard_bp.route('/admin/schools/add', methods=['POST'])
@school_scoped
@role_minimum('admin')
def add_school():
    if g.current_user.role != 'admin':
        abort(403)
    name = request.form.get('name')
    code = request.form.get('code')
    domain = request.form.get('domain')
    
    if not name or not code:
        flash('Name and Code are required.', 'danger')
        return redirect(url_for('dashboard.admin_schools'))
        
    new_school = School(name=name, code=code, domain=domain)
    db.session.add(new_school)
    db.session.commit()
    flash('School added successfully!', 'success')
    return redirect(url_for('dashboard.admin_schools'))

@dashboard_bp.route('/admin/schools/toggle/<int:school_id>', methods=['POST'])
@school_scoped
@role_minimum('admin')
def toggle_school(school_id):
    if g.current_user.role != 'admin':
        abort(403)
    school = School.query.get_or_404(school_id)
    school.is_active = not school.is_active
    db.session.commit()
    status = 'activated' if school.is_active else 'suspended'
    flash(f'School {school.name} has been {status}.', 'info')
    return redirect(url_for('dashboard.admin_schools'))

# --- Sections Management ---
@dashboard_bp.route('/admin/sections')
@school_scoped
@role_minimum('admin')
def admin_sections():
    if g.current_user.role == 'admin':
        sections = Section.query.all()
        schools = School.query.all()
    else:
        sections = Section.query.filter_by(school_id=g.school_id).all()
        schools = [g.current_user.school]
    return render_template('dashboard/admin_sections.html', sections=sections, schools=schools)

@dashboard_bp.route('/admin/sections/add', methods=['POST'])
@school_scoped
@role_minimum('admin')
def add_section():
    school_id = request.form.get('school_id', type=int)
    name = request.form.get('name')
    code = request.form.get('code')
    batch_year = request.form.get('batch_year', type=int)

    if g.current_user.role != 'admin' and school_id != g.school_id:
        abort(403)

    new_section = Section(school_id=school_id, name=name, code=code, batch_year=batch_year)
    db.session.add(new_section)
    db.session.commit()
    flash('Section added successfully!', 'success')
    return redirect(url_for('dashboard.admin_sections'))

# --- Accounts Management ---
@dashboard_bp.route('/admin/accounts')
@school_scoped
@role_minimum('admin')
def admin_accounts():
    if g.current_user.role == 'admin':
        users = User.query.all()
        schools = School.query.all()
    else:
        users = User.query.filter_by(school_id=g.school_id).all()
        schools = [g.current_user.school]
    return render_template('dashboard/admin_accounts.html', users=users, schools=schools)

@dashboard_bp.route('/admin/accounts/toggle/<int:user_id>', methods=['POST'])
@school_scoped
@role_minimum('admin')
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if g.current_user.role != 'admin' and user.school_id != g.school_id:
        abort(403)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.name} has been {status}.', 'info')
    return redirect(url_for('dashboard.admin_accounts'))

# --- Early Warning System ---
@dashboard_bp.route('/early-warning')
@school_scoped
@role_minimum('dean')
def early_warning():
    # Identify students with low attendance (< 75%) or low CGPA (< 1.5)
    at_risk_students = []
    
    # Check CGPA
    # Note: Student model is already imported at the top of the file
    low_cgpa_students = Student.query.join(User).filter(
        User.school_id == g.school_id,
        Student.cgpa < 1.5
    ).all()
    
    for s in low_cgpa_students:
        at_risk_students.append({
            'user': s.user,
            'reason': 'Low CGPA',
            'value': f"{s.cgpa:.2f}"
        })
        
    return render_template('dashboard/early_warning.html', at_risk_students=at_risk_students)

# --- Settings ---
@dashboard_bp.route('/admin/settings')
@school_scoped
@role_minimum('admin')
def admin_settings():
    return render_template('dashboard/admin_settings.html')
