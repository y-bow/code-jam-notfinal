from app import app
from models import db, User, Student, Teacher, Course, Enrollment
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt(app)

def seed_db():
    with app.app_context():
        # Create all tables
        db.metadata.drop_all(bind=db.engine)
        db.create_all()

        print("Tables created.")

        # Seed Users
        # 1 Admin
        admin_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
        admin = User(email='admin@upc.edu', password_hash=admin_pw, role='admin', name='Super Admin')

        # 2 Teachers
        teacher1_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
        teacher1_user = User(email='prof.smith@upc.edu', password_hash=teacher1_pw, role='teacher', name='Prof. John Smith')
        teacher2_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
        teacher2_user = User(email='prof.davis@upc.edu', password_hash=teacher2_pw, role='teacher', name='Prof. Sarah Davis')

        # 4 Students
        student1_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
        student1_user = User(email='vaibhav.b-29@scds.saiuniversity.edu.in', password_hash=student1_pw, role='student', name='Vaibhav B')
        
        student2_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
        student2_user = User(email='sharanpranav.a-29@scds.saiuniversity.edu.in', password_hash=student2_pw, role='student', name='Sharanpranav A')

        student3_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
        student3_user = User(email='harshitha.b-29@scds.saiuniversity.edu.in', password_hash=student3_pw, role='student', name='Harshitha B')

        student4_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
        student4_user = User(email='ruddhima.p-29@scds.saiuniversity.edu.in', password_hash=student4_pw, role='student', name='Ruddhima P')

        db.session.add_all([admin, teacher1_user, teacher2_user, student1_user, student2_user, student3_user, student4_user])
        db.session.commit()

        # Seed Teacher Profiles
        t1 = Teacher(user_id=teacher1_user.id, department='Computer Science', office_hours='Mon/Wed 10am-12pm')
        t2 = Teacher(user_id=teacher2_user.id, department='Mathematics', office_hours='Tue/Thu 2pm-4pm')
        db.session.add_all([t1, t2])
        db.session.commit()

        # Seed Student Profiles
        s1 = Student(user_id=student1_user.id, enrollment_year=2025, major='Computer Science')
        s2 = Student(user_id=student2_user.id, enrollment_year=2025, major='Computer Science')
        s3 = Student(user_id=student3_user.id, enrollment_year=2025, major='Computer Science')
        s4 = Student(user_id=student4_user.id, enrollment_year=2025, major='Computer Science')
        db.session.add_all([s1, s2, s3, s4])
        db.session.commit()

        # Seed Courses
        c1 = Course(name='Introduction to Programming', code='CS101', teacher_id=teacher1_user.id, credits=3)
        c2 = Course(name='Data Structures', code='CS201', teacher_id=teacher1_user.id, credits=4)
        c3 = Course(name='Calculus I', code='MATH101', teacher_id=teacher2_user.id, credits=3)
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        # Seed Enrollments (all students enrolled in all courses)
        enrollments = []
        for student in [student1_user, student2_user, student3_user, student4_user]:
            for course in [c1, c2, c3]:
                enrollments.append(Enrollment(student_id=student.id, course_id=course.id))
        db.session.add_all(enrollments)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_db()
