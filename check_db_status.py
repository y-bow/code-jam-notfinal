from app import create_app
from app.models import db, Section, Course, TimetableEntry

app = create_app()
with app.app_context():
    s3 = Section.query.filter_by(code='SCDS-CS-S3').first()
    print(f'Section 3: {s3}')
    if s3:
        print(f'Section 3 ID: {s3.id}')
        existing_entries = TimetableEntry.query.filter_by(section_id=s3.id).all()
        print(f'Existing Timetable Entries for Section 3: {len(existing_entries)}')
    else:
        print('Section 3 NOT FOUND!')
        all_sections = Section.query.all()
        print(f'All sections: {[s.code for s in all_sections]}')
    
    all_courses = Course.query.all()
    print(f'Total Courses in DB: {len(all_courses)}')
    for c in all_courses:
        print(f' - {c.name} ({c.code})')
