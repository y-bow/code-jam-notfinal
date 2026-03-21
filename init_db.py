from app import create_app
from app.models import (
    db, User, Student, Teacher, School, Section,
    Course, Enrollment, Announcement, TimetableEntry, bcrypt,
    TeacherTodo, TeacherRating, Message, Internship, LostFoundItem,
    Club, ExternalEvent, ProfessorAssistant, ClassRepNomination
)
from datetime import datetime, timedelta

app = create_app()

def seed_db():
    with app.app_context():
        # Drop and recreate all tables
        db.metadata.drop_all(bind=db.engine)
        db.create_all()
        print("Tables created.")

        # =====================================================================
        # 1. SCHOOLS
        # =====================================================================
        apex = School(
            name='Apex Institute of Technology',
            code='APEX',
            domain='apex.edu'
        )
        greenfield = School(
            name='Greenfield University',
            code='GU',
            domain='greenfield.edu'
        )
        db.session.add_all([apex, greenfield])
        db.session.commit()

        # =====================================================================
        # 2. SECTIONS
        # =====================================================================
        # Apex Sections
        apex_sec1 = Section(school_id=apex.id, name='CSE Section A', code='CSE-A', batch_year=2026)
        apex_sec2 = Section(school_id=apex.id, name='CSE Section B', code='CSE-B', batch_year=2026)
        
        # Greenfield Sections
        gu_sec1 = Section(school_id=greenfield.id, name='Biology Group 1', code='BIO-1', batch_year=2026)
        
        db.session.add_all([apex_sec1, apex_sec2, gu_sec1])
        db.session.commit()

        # =====================================================================
        # 3. USERS
        # =====================================================================
        pw = bcrypt.generate_password_hash('password123').decode('utf-8')

        # GLOBAL ADMIN (Platform Owner)
        platform_owner = User(
            school_id=None, 
            email='owner@hive-lms.com',
            password_hash=pw, 
            role='admin', 
            name='HIVE Platform Owner', 
            must_change_password=True
        )
        
        # APEX USERS
        apex_dean = User(
            school_id=apex.id, 
            email='dean@apex.edu',
            password_hash=pw, 
            role='dean', 
            name='Dr. Alice Dean', 
            must_change_password=True
        )
        apex_prof1 = User(
            school_id=apex.id, 
            email='j.smith@apex.edu',
            password_hash=pw, 
            role='professor', 
            name='Prof. John Smith', 
            must_change_password=True
        )
        apex_prof2 = User(
            school_id=apex.id, 
            email='e.brown@apex.edu',
            password_hash=pw, 
            role='professor', 
            name='Prof. Emily Brown', 
            must_change_password=True
        )
        apex_asst_prof = User(
            school_id=apex.id, 
            email='asst.lee@apex.edu',
            password_hash=pw, 
            role='assistant_professor', 
            name='Asst. Prof. David Lee', 
            must_change_password=True
        )
        apex_student = User(
            school_id=apex.id, 
            email='student.alex@apex.edu',
            password_hash=pw, 
            role='student', 
            name='Alex Student', 
            must_change_password=True
        )
        apex_cr = User(
            school_id=apex.id, 
            email='chris.rep@apex.edu',
            password_hash=pw, 
            role='class_rep', 
            name='Chris Rep', 
            must_change_password=True
        )

        # GREENFIELD USERS
        gu_dean = User(
            school_id=greenfield.id, 
            email='dean@greenfield.edu',
            password_hash=pw, 
            role='dean', 
            name='Dr. Sarah Greenfield', 
            must_change_password=True
        )
        gu_prof1 = User(
            school_id=greenfield.id, 
            email='m.wilson@greenfield.edu',
            password_hash=pw, 
            role='professor', 
            name='Prof. Mark Wilson', 
            must_change_password=True
        )
        gu_student = User(
            school_id=greenfield.id, 
            email='sam.jones@greenfield.edu',
            password_hash=pw, 
            role='student', 
            name='Sam Jones', 
            must_change_password=True
        )

        db.session.add_all([
            platform_owner, 
            apex_dean, apex_prof1, apex_prof2, apex_asst_prof, apex_student, apex_cr,
            gu_dean, gu_prof1, gu_student
        ])
        db.session.commit()

        # =====================================================================
        # 4. PROFILES
        # =====================================================================
        db.session.add_all([
            # Apex Profiles
            Teacher(user_id=apex_prof1.id, department='Computer Science'),
            Teacher(user_id=apex_prof2.id, department='Mathematics'),
            Teacher(user_id=apex_asst_prof.id, department='Computer Science'),
            Student(user_id=apex_student.id, section_id=apex_sec1.id, enrollment_year=2026, cgpa=8.5),
            Student(user_id=apex_cr.id, section_id=apex_sec1.id, enrollment_year=2026, cgpa=9.2),
            
            # Greenfield Profiles
            Teacher(user_id=gu_prof1.id, department='Biology'),
            Student(user_id=gu_student.id, section_id=gu_sec1.id, enrollment_year=2026, cgpa=7.8),
        ])
        db.session.commit()

        # =====================================================================
        # 5. COURSES
        # =====================================================================
        # Apex Courses
        ds_course = Course(section_id=apex_sec1.id, name='Data Structures', code='CS101', teacher_id=apex_prof1.id, credits=4)
        algo_course = Course(section_id=apex_sec1.id, name='Algorithms', code='CS102', teacher_id=apex_prof1.id, credits=4)
        math_course = Course(section_id=apex_sec1.id, name='Calculus I', code='MA101', teacher_id=apex_prof2.id, credits=3)
        
        # Greenfield Courses
        bio_course = Course(section_id=gu_sec1.id, name='Molecular Biology', code='BIO201', teacher_id=gu_prof1.id, credits=4)
        
        db.session.add_all([ds_course, algo_course, math_course, bio_course])
        db.session.commit()

        # =====================================================================
        # 6. ENROLLMENTS
        # =====================================================================
        db.session.add_all([
            Enrollment(student_id=apex_student.id, course_id=ds_course.id),
            Enrollment(student_id=apex_student.id, course_id=math_course.id),
            Enrollment(student_id=apex_cr.id, course_id=ds_course.id),
            Enrollment(student_id=gu_student.id, course_id=bio_course.id),
        ])
        db.session.commit()

        # =====================================================================
        # 7. TIMETABLE
        # =====================================================================
        db.session.add_all([
            TimetableEntry(
                section_id=apex_sec1.id, course_id=ds_course.id, day=0, 
                start_time='09:00 AM', end_time='10:30 AM', title='Data Structures', 
                room='L-101', color='var(--primary-color)', teacher='Prof. John Smith', period='P1'
            ),
            TimetableEntry(
                section_id=gu_sec1.id, course_id=bio_course.id, day=0, 
                start_time='10:00 AM', end_time='11:30 AM', title='Molecular Biology', 
                room='B-402', color='var(--success-color)', teacher='Prof. Mark Wilson', period='P1'
            )
        ])
        db.session.commit()

        print("Database seeded successfully with two universities and fictional data!")

if __name__ == '__main__':
    seed_db()
