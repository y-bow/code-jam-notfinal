from app import create_app
from app.models import db, Section, Course, TimetableEntry, User
from datetime import datetime

app = create_app()

def seed_timetable():
    with app.app_context():
        # 1. Find Section 3
        section = Section.query.filter_by(code='SCDS-CS-S3').first()
        if not section:
            print("ERROR: Section SCDS-CS-S3 not found. Run seed.py first.")
            return
        
        print(f"Found Section 3: ID={section.id}")

        # 2. Find Assistant Professor / Professor for teaching
        # We'll use the 'professor' user as default teacher for these courses
        teacher = User.query.filter_by(email='professor@scds.saiuniversity.edu.in').first()
        if not teacher:
            # Fallback to any teacher if specific one not found
            teacher = User.query.filter(User.role.in_(['professor', 'assistant_professor'])).first()
        
        if not teacher:
            print("ERROR: No professor/assistant professor found. Run seed.py first.")
            return

        print(f"Using Teacher: {teacher.name} (ID={teacher.id})")

        # 3. Create Courses for Section 3
        courses_to_create = [
            ("Discrete Mathematics", "CS-301", 4),
            ("Indian Constitution and Democracy", "ICD-101", 2),
            ("Python and Data Structure (LAB)", "CS-302L", 2),
            ("Introduction to Data Structures", "CS-302", 4),
            ("Environment and Sustainability", "ES-101", 2),
            ("Programming in Python", "CS-303", 4),
        ]

        section_courses = {}
        for name, code, credits in courses_to_create:
            existing = Course.query.filter_by(section_id=section.id, code=code).first()
            if existing:
                print(f"Skipping: Course {code} already exists.")
                section_courses[name] = existing
            else:
                course = Course(
                    section_id=section.id,
                    name=name,
                    code=code,
                    teacher_id=teacher.id,
                    credits=credits
                )
                db.session.add(course)
                db.session.flush()
                section_courses[name] = course
                print(f"Added Course: {name} ({code})")

        # 4. Define Timetable Entries
        # Days: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday
        entries_data = [
            # Monday
            (0, "10:40 AM", "12:10 PM", "Discrete Mathematics", "AB2 - 203", "#cfe2f3"),
            (0, "02:15 PM", "03:40 PM", "Indian Constitution and Democracy", "AB2 - 202", "#ead1dc"),
            (0, "03:50 PM", "05:15 PM", "Python and Data Structure (LAB)", "Computer Lab - AB1 - First Floor", "#b45f06"),
            
            # Tuesday
            (1, "09:00 AM", "10:30 AM", "Introduction to Data Structures", "AB1 - 101", "#f9cb9c"),
            (1, "12:15 PM", "01:45 PM", "Environment and Sustainability", "AB1 - Moot Court Hall", "#d9ead3"),
            
            # Wednesday
            (2, "09:00 AM", "10:30 AM", "Discrete Mathematics", "AB2 - 203", "#cfe2f3"),
            (2, "02:15 PM", "03:40 PM", "Indian Constitution and Democracy", "AB2 - 207", "#ead1dc"),
            
            # Thursday
            (3, "09:00 AM", "10:30 AM", "Programming in Python", "AB2 - 207", "#fce5cd"),
            (3, "12:20 PM", "01:40 PM", "Python and Data Structure (LAB)", "Computer Lab - AB1 - First Floor", "#b45f06"),
            
            # Friday
            (4, "10:40 AM", "12:10 PM", "Programming in Python", "AB2 - 202", "#fce5cd"),
            (4, "02:15 PM", "03:40 PM", "Introduction to Data Structures", "AB2 - 202", "#f9cb9c"),
            (4, "03:50 PM", "05:15 PM", "Environment and Sustainability", "AB2 - 202", "#d9ead3"),
        ]

        # Clear existing timetable for this section to avoid duplicates
        TimetableEntry.query.filter_by(section_id=section.id).delete()
        print(f"Cleared existing timetable entries for Section {section.id}")

        for day, start, end, title, room, color in entries_data:
            course = section_courses.get(title)
            entry = TimetableEntry(
                section_id=section.id,
                course_id=course.id if course else None,
                day=day,
                start_time=start,
                end_time=end,
                title=title,
                teacher=teacher.name,
                room=room,
                color=color,
                status='active'
            )
            db.session.add(entry)
        
        db.session.commit()
        print("\nTimetable for Section 3 seeded successfully!")

if __name__ == "__main__":
    seed_timetable()
