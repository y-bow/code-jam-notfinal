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
        school = School(
            name='Sai University - School of Computing and Data Science',
            code='SCDS',
            domain='scds.saiuniversity.edu.in',
            logo_url='https://scds.saiuniversity.edu.in/wp-content/uploads/2021/08/SCDS-Logo-Final.png',
            accent_color='#1E40AF'
        )
        db.session.add(school)
        db.session.commit()

        # =====================================================================
        # 2. SECTIONS
        # =====================================================================
        sec1 = Section(school_id=school.id, name='Section 1', code='SEC-1', batch_year=2025)
        sec2 = Section(school_id=school.id, name='Section 2', code='SEC-2', batch_year=2025)
        db.session.add_all([sec1, sec2])
        db.session.commit()

        # =====================================================================
        # 3. USERS (Exactly 6 Roles)
        # =====================================================================
        pw = bcrypt.generate_password_hash('password123').decode('utf-8')

        # ROLE 6: ADMIN (Level 99 - Global)
        admin = User(school_id=None, email='admin@hive.lms',
                     password_hash=pw, role='admin', name='HIVE Global Admin', must_change_password=False)
        
        # ROLE 5: DEAN (Level 5)
        dean = User(school_id=school.id, email='dean@scds.saiuniversity.edu.in',
                    password_hash=pw, role='dean', name='Dr. Sarah Dean', must_change_password=False)
        
        # ROLE 4: PROFESSOR (Level 4)
        prof_nitish = User(school_id=school.id, email='nitish.r@saiuniversity.edu.in',
                                password_hash=pw, role='professor', name='Prof. Nitish Rana', must_change_password=False)
        prof_megha = User(school_id=school.id, email='megha.k@saiuniversity.edu.in',
                              password_hash=pw, role='professor', name='Prof. Megha Kapoor', must_change_password=False)
        
        # ROLE 3: ASSISTANT PROFESSOR (Level 3)
        assistant_prof = User(school_id=school.id, email='assistant@saiuniversity.edu.in',
                              password_hash=pw, role='assistant_professor', name='Asst. Prof. Alex', must_change_password=False)
        
        # ROLE 2: CLASS REP (Level 2)
        class_rep = User(school_id=school.id, email='rep@scds.saiuniversity.edu.in',
                       password_hash=pw, role='class_rep', name='Sharan (Class Rep)', must_change_password=False)
        
        # ROLE 1: STUDENT (Level 1)
        student1 = User(school_id=school.id, email='vaibhav.b-29@scds.saiuniversity.edu.in',
                       password_hash=pw, role='student', name='Vaibhav Student', must_change_password=False)
        
        db.session.add_all([admin, dean, prof_nitish, prof_megha, assistant_prof, class_rep, student1])
        db.session.commit()

        # =====================================================================
        # 4. PROFILES
        # =====================================================================
        db.session.add_all([
            Teacher(user_id=prof_nitish.id, department='Computer Science'),
            Teacher(user_id=prof_megha.id, department='Humanities'),
            Teacher(user_id=assistant_prof.id, department='Computer Science'),
            Student(user_id=class_rep.id, section_id=sec1.id, enrollment_year=2025, cgpa=9.0),
            Student(user_id=student1.id, section_id=sec1.id, enrollment_year=2025, cgpa=8.5),
        ])
        db.session.commit()

        # =====================================================================
        # 5. COURSES & ASSISTANTS
        # =====================================================================
        course1 = Course(section_id=sec1.id, name='Data Structures', code='CS201', teacher_id=prof_nitish.id, credits=4)
        course2 = Course(section_id=sec1.id, name='Indian Constitution', code='POL101', teacher_id=prof_megha.id, credits=3)
        db.session.add_all([course1, course2])
        db.session.commit()

        # Assign Assistant to course1
        pa_entry = ProfessorAssistant(course_id=course1.id, professor_id=prof_nitish.id, assistant_teacher_id=assistant_prof.id)
        db.session.add(pa_entry)
        db.session.commit()

        # =====================================================================
        # 6. ENROLLMENTS
        # =====================================================================
        db.session.add_all([
            Enrollment(student_id=student1.id, course_id=course1.id),
            Enrollment(student_id=student1.id, course_id=course2.id),
            Enrollment(student_id=class_rep.id, course_id=course1.id),
            Enrollment(student_id=class_rep.id, course_id=course2.id),
        ])
        db.session.commit()

        # =====================================================================
        # 7. TIMETABLE
        # =====================================================================
        db.session.add_all([
            TimetableEntry(section_id=sec1.id, course_id=course1.id, day=0, start_time='09:00 AM', end_time='10:30 AM', title='Data Structures', room='AB1-101', color='var(--success-color)', teacher='Prof. Nitish Rana', period='P1'),
            TimetableEntry(section_id=sec1.id, course_id=course2.id, day=0, start_time='11:00 AM', end_time='12:30 PM', title='Indian Constitution', room='AB1-102', color='var(--primary-color)', teacher='Prof. Megha Kapoor', period='P2')
        ])
        db.session.commit()

        print("Database seeded successfully with 6 roles!")

if __name__ == '__main__':
    seed_db()
