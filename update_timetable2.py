import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, TimetableEntry, Section

with app.app_context():
    # Find Section 2
    sec2 = Section.query.filter_by(code='SEC-2').first()
    if not sec2:
        print("Section 2 not found!")
        sys.exit(1)
        
    # Clear existing timetable for sec2 just in case
    TimetableEntry.query.filter_by(section_id=sec2.id).delete()

    sec2_timetable = [
        # Monday
        (0, '09:30 AM', '10:40 AM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)'),
        (0, '10:40 AM', '12:10 PM', 'Indian Constitution and Democracy', 'AB2 - 202', '#a78bfa'),
        (0, '12:15 PM', '01:45 PM', 'Environment and Sustainability', 'AB2 - Mini Auditorium', 'var(--success-color)'),
        # Tuesday
        (1, '09:00 AM', '10:30 AM', 'Programming in Python', 'AB2 - 202', '#f472b6'),
        (1, '12:20 PM', '01:40 PM', 'Python and Data Structure (LAB)', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)'),
        # Wednesday
        (2, '10:00 AM', '11:30 AM', 'Indian Constitution and Democracy', 'AB2 - 101', '#a78bfa'),
        (2, '12:40 PM', '02:05 PM', 'Introduction to Data Structures', 'AB1 - Moot Court Hall', '#ea580c'),
        (2, '02:15 PM', '03:40 PM', 'Environment and Sustainability', 'AB2 - Mini Auditorium', 'var(--success-color)'),
        # Thursday
        (3, '10:00 AM', '11:30 AM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)'),
        (3, '01:40 PM', '03:05 PM', 'Programming in Python', 'AB2 - 101', '#f472b6'),
        # Friday
        (4, '10:40 AM', '12:10 PM', 'Python and Data Structure (LAB)', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)'),
        (4, '12:40 PM', '02:05 PM', 'Introduction to Data Structures', 'AB2 - 202', 'var(--warning-color)'),
    ]
    
    for day, st, et, title, room, color in sec2_timetable:
        db.session.add(TimetableEntry(section_id=sec2.id, day=day,
                        start_time=st, end_time=et, title=title, room=room, color=color))
                    
    db.session.commit()
    print("Section 2 timetable updated")
