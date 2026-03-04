from app import app
from models import (
    db, User, Student, Teacher, School, Section,
    Course, Enrollment, Announcement, TimetableEntry
)
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt(app)


def seed_db():
    with app.app_context():
        # Drop and recreate all tables
        db.metadata.drop_all(bind=db.engine)
        db.create_all()
        print("Tables created.")

        # =====================================================================
        # 1. SCHOOL
        # =====================================================================
        school = School(
            name='Sai University - School of Computing and Data Science',
            code='SCDS',
            domain='scds.saiuniversity.edu.in'
        )
        db.session.add(school)
        db.session.commit()
        print(f"School created: {school.name}")

        # =====================================================================
        # 2. SECTIONS
        # =====================================================================
        sec2 = Section(school_id=school.id, name='Section 2', code='SEC-2', batch_year=2025)
        sec3 = Section(school_id=school.id, name='Section 3', code='SEC-3', batch_year=2025)
        sec4 = Section(school_id=school.id, name='Section 4', code='SEC-4', batch_year=2025)
        db.session.add_all([sec2, sec3, sec4])
        db.session.commit()
        print(f"Sections created: SEC-2, SEC-3, SEC-4")

        # =====================================================================
        # 3. USERS
        # =====================================================================
        pw = bcrypt.generate_password_hash('password123').decode('utf-8')

        admin = User(school_id=school.id, email='admin@scds.saiuniversity.edu.in',
                     password_hash=pw, role='superadmin', name='Super Admin')
        dean = User(school_id=school.id, email='dean@scds.saiuniversity.edu.in',
                    password_hash=pw, role='dean', name='Dr. Dean Kumar')
        teacher1 = User(school_id=school.id, email='prof.smith@scds.saiuniversity.edu.in',
                        password_hash=pw, role='teacher', name='Prof. John Smith')
        teacher2 = User(school_id=school.id, email='prof.davis@scds.saiuniversity.edu.in',
                        password_hash=pw, role='teacher', name='Prof. Sarah Davis')

        # Students
        vaibhav = User(school_id=school.id, email='vaibhav.b-29@scds.saiuniversity.edu.in',
                       password_hash=pw, role='student', name='Vaibhav B')
        sharan = User(school_id=school.id, email='sharanpranav.a-29@scds.saiuniversity.edu.in',
                      password_hash=pw, role='student', name='Sharanpranav A')
        harshitha = User(school_id=school.id, email='harshitha.b-29@scds.saiuniversity.edu.in',
                         password_hash=pw, role='student', name='Harshitha B')
        riddhima = User(school_id=school.id, email='ruddhima.p-29@scds.saiuniversity.edu.in',
                        password_hash=pw, role='student', name='Riddhima P')

        all_users = [admin, dean, teacher1, teacher2, vaibhav, sharan, harshitha, riddhima]
        db.session.add_all(all_users)
        db.session.commit()
        print(f"Users created: {len(all_users)}")

        # =====================================================================
        # 4. PROFILES
        # =====================================================================
        t1 = Teacher(user_id=teacher1.id, department='Computer Science', office_hours='Mon/Wed 10am-12pm')
        t2 = Teacher(user_id=teacher2.id, department='Mathematics', office_hours='Tue/Thu 2pm-4pm')
        db.session.add_all([t1, t2])

        # Student profiles — assigned to correct sections
        student_sections = [
            (vaibhav, sec3),      # Vaibhav B → Section 3
            (sharan, sec4),       # Sharanpranav A → Section 4
            (harshitha, sec2),    # Harshitha B → Section 2
            (riddhima, sec2),     # Riddhima P → Section 2
        ]
        for user, section in student_sections:
            db.session.add(Student(user_id=user.id, section_id=section.id,
                                   enrollment_year=2025, major='Computer Science'))
        db.session.commit()
        print("Profiles created.")

        # =====================================================================
        # 5. COURSES (under sections)
        # =====================================================================
        # Section 3 courses
        s3_courses = [
            Course(section_id=sec3.id, name='Discrete Mathematics', code='MATH201', teacher_id=teacher2.id, credits=4),
            Course(section_id=sec3.id, name='Indian Constitution and Democracy', code='POL101', teacher_id=teacher2.id, credits=3),
            Course(section_id=sec3.id, name='Python and Data Structure', code='CS102', teacher_id=teacher1.id, credits=4),
            Course(section_id=sec3.id, name='Introduction to Data Structures', code='CS201', teacher_id=teacher1.id, credits=4),
            Course(section_id=sec3.id, name='Programming in Python', code='CS101', teacher_id=teacher1.id, credits=3),
            Course(section_id=sec3.id, name='Environment and Sustainability', code='ENV101', teacher_id=teacher2.id, credits=3),
        ]
        db.session.add_all(s3_courses)

        # Section 4 courses
        s4_courses = [
            Course(section_id=sec4.id, name='Indian Constitution and Democracy', code='POL101', teacher_id=teacher2.id, credits=3),
            Course(section_id=sec4.id, name='Discrete Mathematics', code='MATH201', teacher_id=teacher2.id, credits=4),
            Course(section_id=sec4.id, name='PDS Lab Sec4', code='CS102L', teacher_id=teacher1.id, credits=4),
            Course(section_id=sec4.id, name='Introduction to Data Structures', code='CS201', teacher_id=teacher1.id, credits=4),
            Course(section_id=sec4.id, name='Principles of Economics (SAS)', code='ECO101', teacher_id=teacher2.id, credits=3),
        ]
        db.session.add_all(s4_courses)
        db.session.commit()
        print("Courses created.")

        # =====================================================================
        # 6. ENROLLMENTS
        # =====================================================================
        # Enroll Vaibhav in all Sec3 courses
        for c in s3_courses:
            db.session.add(Enrollment(student_id=vaibhav.id, course_id=c.id))
        # Enroll Sharan in all Sec4 courses
        for c in s4_courses:
            db.session.add(Enrollment(student_id=sharan.id, course_id=c.id))
        db.session.commit()
        print("Enrollments created.")

        # =====================================================================
        # 7. TIMETABLE ENTRIES
        # =====================================================================
        # --- Section 3 timetable ---
        sec3_timetable = [
            # Monday
            (0, '10:40 AM', '12:10 PM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)'),
            (0, '02:15 PM', '03:40 PM', 'Indian Constitution and Democracy', 'AB2 - 202', '#a78bfa'),
            (0, '03:50 PM', '05:15 PM', 'Python and Data Structure (LAB)', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)'),
            # Tuesday
            (1, '09:00 AM', '10:30 AM', 'Introduction to Data Structures', 'AB1 - 101', 'var(--success-color)'),
            (1, '12:15 PM', '01:45 PM', 'Environment and Sustainability', 'AB1 - Moot Court Hall', 'var(--warning-color)'),
            # Wednesday
            (2, '09:00 AM', '10:30 AM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)'),
            (2, '02:15 PM', '03:40 PM', 'Indian Constitution and Democracy', 'AB2 - 207', '#a78bfa'),
            # Thursday
            (3, '09:00 AM', '10:30 AM', 'Programming in Python', 'AB2 - 207', '#f472b6'),
            (3, '12:20 PM', '01:40 PM', 'Python and Data Structure (LAB)', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)'),
            # Friday
            (4, '10:40 AM', '12:10 PM', 'Programming in Python', 'AB2 - 202', '#f472b6'),
            (4, '02:15 PM', '03:40 PM', 'Introduction to Data Structures', 'AB2 - 202', 'var(--success-color)'),
            (4, '03:50 PM', '05:15 PM', 'Environment and Sustainability', 'AB2 - 202', 'var(--warning-color)'),
        ]
        for day, st, et, title, room, color in sec3_timetable:
            db.session.add(TimetableEntry(section_id=sec3.id, day=day,
                           start_time=st, end_time=et, title=title, room=room, color=color))

        # --- Section 4 timetable ---
        sec4_timetable = [
            # Monday
            (0, '09:00 AM', '10:30 AM', 'Indian Constitution & Democracy', 'AB2 - 202', '#a78bfa'),
            # Tuesday
            (1, '09:00 AM', '10:30 AM', 'Discrete Mathematics', 'AB2 - 202', 'var(--primary-color)'),
            # Wednesday
            (2, '09:00 AM', '10:30 AM', 'PDS Lab Sec4', 'AB1 Comp Lab', 'var(--accent-color)'),
            # Thursday
            (3, '09:00 AM', '10:30 AM', 'Introduction to Data Structures', 'AB2 - 101', 'var(--success-color)'),
            (3, '10:40 AM', '12:10 PM', 'PDS Lab Sec4', 'AB1 Comp Lab', 'var(--accent-color)'),
            (3, '12:40 PM', '02:05 PM', 'Indian Constitution & Democracy', 'AB1 - 104', '#a78bfa'),
            # Friday
            (4, '09:00 AM', '10:30 AM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)'),
            (4, '12:40 PM', '02:05 PM', 'Principles of Economics (SAS)', 'AB1 - 101', 'var(--warning-color)'),
        ]
        for day, st, et, title, room, color in sec4_timetable:
            db.session.add(TimetableEntry(section_id=sec4.id, day=day,
                           start_time=st, end_time=et, title=title, room=room, color=color))

        # Section 2 timetable — placeholder (pending user input)
        # Will be populated once timetable data is provided

        db.session.commit()
        print("Timetable entries seeded.")

        # =====================================================================
        # 8. SAMPLE ANNOUNCEMENTS
        # =====================================================================
        a1 = Announcement(school_id=school.id, course_id=None, teacher_id=dean.id,
                          title='Welcome to the new semester!',
                          body='Classes begin on March 10. Check your timetable for details.')
        a2 = Announcement(school_id=school.id, course_id=s3_courses[0].id, teacher_id=teacher2.id,
                          title='Discrete Math Quiz on Friday',
                          body='Chapter 1-3 covered. Bring calculators.', urgent=True)
        db.session.add_all([a1, a2])
        db.session.commit()

        print("\nDatabase seeded successfully!")
        print("\n=== Login Credentials (password: password123) ===")
        print(f"  Admin:      admin@scds.saiuniversity.edu.in")
        print(f"  Dean:       dean@scds.saiuniversity.edu.in")
        print(f"  Teacher1:   prof.smith@scds.saiuniversity.edu.in")
        print(f"  Teacher2:   prof.davis@scds.saiuniversity.edu.in")
        print(f"  Vaibhav B   (SEC-3): vaibhav.b-29@scds.saiuniversity.edu.in")
        print(f"  Sharanpranav A (SEC-4): sharanpranav.a-29@scds.saiuniversity.edu.in")
        print(f"  Harshitha B (SEC-2): harshitha.b-29@scds.saiuniversity.edu.in")
        print(f"  Riddhima P  (SEC-2): ruddhima.p-29@scds.saiuniversity.edu.in")


if __name__ == '__main__':
    seed_db()
