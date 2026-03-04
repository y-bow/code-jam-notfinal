import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, TimetableEntry, Section

with app.app_context():
    # Find Section 3
    sec3 = Section.query.filter_by(code='SEC-3').first()
    if not sec3:
        print("Section 3 not found! Creating it...")
        # Since I saw it has ID=1 from my query earlier, it should exist, 
        # but just in case, the query gave (1, 'Section 3', 'SEC-3')
        sec3 = Section(school_id=1, name='Section 3', code='SEC-3', batch_year=2026)
        db.session.add(sec3)
        db.session.commit()
        
    # Clear existing timetable for sec3
    TimetableEntry.query.filter_by(section_id=sec3.id).delete()

    sec3_timetable = [
        # Monday
        (0, '10:40 AM', '12:10 PM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)'),
        (0, '02:15 PM', '03:40 PM', 'Indian Constitution and Democracy', 'AB2 - 202', '#a78bfa'),
        (0, '03:50 PM', '05:15 PM', 'Python and Data Structure (LAB)', 'Computer Lab - AB1 - First Floor', '#d97706'),
        # Tuesday
        (1, '09:00 AM', '10:30 AM', 'Introduction to Data Structures', 'AB1 - 101', '#ea580c'),
        (1, '12:15 PM', '01:45 PM', 'Environment and Sustainability', 'AB1 - Moot Court Hall', 'var(--success-color)'),
        # Wednesday
        (2, '09:00 AM', '10:30 AM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)'),
        (2, '02:15 PM', '03:40 PM', 'Indian Constitution and Democracy', 'AB2 - 207', '#a78bfa'),
        # Thursday
        (3, '09:00 AM', '10:30 AM', 'Programming in Python', 'AB2 - 207', '#f97316'),
        (3, '12:20 PM', '01:40 PM', 'Python and Data Structure (LAB)', 'Computer Lab - AB1 - First Floor', '#d97706'),
        # Friday
        (4, '10:40 AM', '12:10 PM', 'Programming in Python', 'AB2 - 202', '#f97316'),
        (4, '02:15 PM', '03:40 PM', 'Introduction to Data Structures', 'AB2 - 202', '#ea580c'),
        (4, '03:50 PM', '05:15 PM', 'Environment and Sustainability', 'AB2 - 202', 'var(--success-color)'),
    ]
    
    for day, st, et, title, room, color in sec3_timetable:
        db.session.add(TimetableEntry(section_id=sec3.id, day=day,
                        start_time=st, end_time=et, title=title, room=room, color=color))
                    
    db.session.commit()
    print("Section 3 timetable updated successfully.")
