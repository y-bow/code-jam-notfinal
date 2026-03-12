from app import create_app
from app.models import (
    db, User, Student, Teacher, School, Section,
    Course, Enrollment, Announcement, TimetableEntry, bcrypt,
    TeacherTodo, TeacherRating, FriendRequest, Friendship
)
from datetime import datetime

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
            domain='scds.saiuniversity.edu.in'
        )
        school_soai = School(
            name='Sai University - School of Arts and Sciences',
            code='SOAS',
            domain='soas.saiuniversity.edu.in'
        )
        db.session.add_all([school, school_soai])
        db.session.commit()

        # =====================================================================
        # 2. SECTIONS
        # =====================================================================
        sec1 = Section(school_id=school.id, name='Section 1', code='SEC-1', batch_year=2025)
        sec2 = Section(school_id=school.id, name='Section 2', code='SEC-2', batch_year=2025)
        sec3 = Section(school_id=school.id, name='Section 3', code='SEC-3', batch_year=2025)
        sec4 = Section(school_id=school.id, name='Section 4', code='SEC-4', batch_year=2025)
        sec5 = Section(school_id=school.id, name='Section 5', code='SEC-5', batch_year=2025)
        sec_soai_1 = Section(school_id=school_soai.id, name='SOAI Section 1', code='SOAI-SEC1', batch_year=2025)
        db.session.add_all([sec1, sec2, sec3, sec4, sec5, sec_soai_1])
        db.session.commit()

        # =====================================================================
        # 3. USERS
        # =====================================================================
        pw = bcrypt.generate_password_hash('password123').decode('utf-8')

        admin = User(school_id=school.id, email='admin@scds.saiuniversity.edu.in',
                     password_hash=pw, role='admin', name='Super Admin')
        superadmin = User(school_id=school.id, email='super@scds.saiuniversity.edu.in',
                     password_hash=pw, role='superadmin', name='Super User')
        dean = User(school_id=school.id, email='dean@scds.saiuniversity.edu.in',
                    password_hash=pw, role='dean', name='Dr. Dean Kumar')
        teacher1 = User(school_id=school.id, email='prof.smith@scds.saiuniversity.edu.in',
                        password_hash=pw, role='teacher', name='Prof. John Smith')
        teacher2 = User(school_id=school.id, email='prof.davis@scds.saiuniversity.edu.in',
                        password_hash=pw, role='teacher', name='Prof. Sarah Davis')
        teacher_nitish = User(school_id=school.id, email='nitish@scds.saiuniversity.edu.in',
                              password_hash=pw, role='teacher', name='Nitish')
        teacher_megha = User(school_id=school.id, email='megha.k@scds.saiuniversity.edu.in',
                             password_hash=pw, role='teacher', name='Megha Kapoor')
        teacher_gopi = User(school_id=school.id, email='gopi@scds.saiuniversity.edu.in',
                            password_hash=pw, role='teacher', name='Gopi')
        teacher_beaula = User(school_id=school.id, email='beaula@scds.saiuniversity.edu.in',
                              password_hash=pw, role='teacher', name='Beaula')
        teacher_arjun = User(school_id=school.id, email='arjun@scds.saiuniversity.edu.in',
                             password_hash=pw, role='teacher', name='Arjun')

        # Students
        vaibhav = User(school_id=school.id, email='vaibhav.b-29@scds.saiuniversity.edu.in',
                       password_hash=pw, role='student', name='Vaibhav B')
        sharan = User(school_id=school.id, email='sharanpranav.a-29@scds.saiuniversity.edu.in',
                      password_hash=pw, role='student', name='Sharanpranav A')
        harshitha = User(school_id=school.id, email='harshitha.b-29@scds.saiuniversity.edu.in',
                         password_hash=pw, role='student', name='Harshitha B')
        riddhima = User(school_id=school.id, email='riddhima.p-29@scds.saiuniversity.edu.in',
                        password_hash=pw, role='student', name='Riddhima P')
        saiteja = User(school_id=school.id, email='saiteja.m-29@scds.saiuniversity.edu.in',
                       password_hash=pw, role='student', name='Mannemala Charan Sai Teja')
        balaaditya = User(school_id=school.id, email='balaaditya.t-29@scds.saiuniversity.edu.in',
                         password_hash=pw, role='student', name='Balaaditya T')

        # SOAI Users
        greeta = User(school_id=school_soai.id, email='greeta@soai.saiuniversity.edu.in',
                       password_hash=pw, role='teacher', name='Greeta')
        siddharth = User(school_id=school_soai.id, email='siddharth@soai.saiuniversity.edu.in',
                         password_hash=pw, role='teacher', name='Siddharth')
        siddanth = User(school_id=school_soai.id, email='siddanth@soai.saiuniversity.edu.in',
                        password_hash=pw, role='teacher', name='Siddanth')
        pankaj = User(school_id=school_soai.id, email='pankaj@soai.saiuniversity.edu.in',
                      password_hash=pw, role='teacher', name='Pankaj')
        arun_kumar = User(school_id=school_soai.id, email='arun.kumar@soai.saiuniversity.edu.in',
                           password_hash=pw, role='teacher', name='Arun Kumar')
        sadhana = User(school_id=school_soai.id, email='sadhana.s@soai.saiuniversity.edu.in',
                        password_hash=pw, role='student', name='Sadhana Srinivasan')

        all_users = [admin, superadmin, dean, teacher1, teacher2, teacher_nitish, teacher_megha, teacher_gopi, 
                     teacher_beaula, teacher_arjun, vaibhav, sharan, harshitha, riddhima, saiteja, 
                     balaaditya, greeta, siddharth, siddanth, pankaj, arun_kumar, sadhana]
        db.session.add_all(all_users)
        db.session.commit()

        # =====================================================================
        # 4. PROFILES
        # =====================================================================
        teachers = [
            Teacher(user_id=teacher1.id, department='Computer Science', office_hours='Mon/Wed 10am-12pm'),
            Teacher(user_id=teacher2.id, department='Mathematics', office_hours='Tue/Thu 2pm-4pm'),
            Teacher(user_id=greeta.id, department='Artificial Intelligence'),
            Teacher(user_id=siddharth.id, department='Humanities'),
            Teacher(user_id=siddanth.id, department='Social Sciences'),
            Teacher(user_id=pankaj.id, department='Computer Science'),
            Teacher(user_id=arun_kumar.id, department='Mathematics'),
            Teacher(user_id=teacher_nitish.id, department='Computer Science'),
            Teacher(user_id=teacher_megha.id, department='Humanities'),
            Teacher(user_id=teacher_gopi.id, department='Environmental Science'),
            Teacher(user_id=teacher_beaula.id, department='Mathematics'),
            Teacher(user_id=teacher_arjun.id, department='Computer Science'),
        ]
        db.session.add_all(teachers)

        student_sections = [
            (vaibhav, sec3), (sharan, sec4), (harshitha, sec2), (riddhima, sec2),
            (saiteja, sec5), (balaaditya, sec1), (sadhana, sec_soai_1)
        ]
        for user, section in student_sections:
            db.session.add(Student(user_id=user.id, section_id=section.id, enrollment_year=2025, major='Computer Science'))
        db.session.commit()

        # =====================================================================
        # 5. COURSES
        # =====================================================================
        s1_courses = [
            Course(section_id=sec1.id, name='Introduction to Data Structures', code='CS201', teacher_id=teacher_nitish.id, credits=4),
            Course(section_id=sec1.id, name='Indian Constitution and Democracy', code='POL101', teacher_id=teacher_megha.id, credits=3),
            Course(section_id=sec1.id, name='Environment and Sustainability', code='ENV101', teacher_id=teacher_gopi.id, credits=3),
            Course(section_id=sec1.id, name='Discrete Mathematics', code='MATH201', teacher_id=teacher_beaula.id, credits=4),
            Course(section_id=sec1.id, name='Programming in Python', code='CS101', teacher_id=teacher_arjun.id, credits=3),
            Course(section_id=sec1.id, name='PDS Lab', code='CS101L', teacher_id=teacher_arjun.id, credits=2),
        ]
        s2_courses = [
            Course(section_id=sec2.id, name='Introduction to Data Structures', code='CS201', teacher_id=teacher1.id, credits=4),
            Course(section_id=sec2.id, name='Discrete Mathematics', code='MATH201', teacher_id=teacher2.id, credits=4),
            Course(section_id=sec2.id, name='Programming in Python', code='CS101', teacher_id=teacher1.id, credits=3),
            Course(section_id=sec2.id, name='Environment and Sustainability', code='ENV101', teacher_id=teacher2.id, credits=3),
            Course(section_id=sec2.id, name='Indian Constitution and Democracy', code='POL101', teacher_id=teacher2.id, credits=3),
        ]
        s3_courses = [
            Course(section_id=sec3.id, name='Discrete Mathematics', code='MATH201', teacher_id=teacher2.id, credits=4),
            Course(section_id=sec3.id, name='Indian Constitution and Democracy', code='POL101', teacher_id=teacher2.id, credits=3),
            Course(section_id=sec3.id, name='Python and Data Structure', code='CS102', teacher_id=teacher1.id, credits=4),
            Course(section_id=sec3.id, name='Introduction to Data Structures', code='CS201', teacher_id=teacher1.id, credits=4),
            Course(section_id=sec3.id, name='Programming in Python', code='CS101', teacher_id=teacher1.id, credits=3),
            Course(section_id=sec3.id, name='Environment and Sustainability', code='ENV101', teacher_id=teacher2.id, credits=3),
        ]
        s4_courses = [
            Course(section_id=sec4.id, name='Indian Constitution and Democracy', code='POL101', teacher_id=teacher2.id, credits=3),
            Course(section_id=sec4.id, name='Discrete Mathematics', code='MATH201', teacher_id=teacher2.id, credits=4),
            Course(section_id=sec4.id, name='PDS Lab Sec4', code='CS102L', teacher_id=teacher1.id, credits=4),
            Course(section_id=sec4.id, name='Introduction to Data Structures', code='CS201', teacher_id=teacher1.id, credits=4),
            Course(section_id=sec4.id, name='Principles of Economics (SAS)', code='ECO101', teacher_id=teacher2.id, credits=3),
        ]
        s5_courses = [
            Course(section_id=sec5.id, name='Introduction to Data Structures', code='CS201', teacher_id=teacher1.id, credits=4),
            Course(section_id=sec5.id, name='Discrete Mathematics', code='MATH201', teacher_id=teacher2.id, credits=4),
            Course(section_id=sec5.id, name='Programming in Python', code='CS101', teacher_id=teacher1.id, credits=3),
            Course(section_id=sec5.id, name='Environment and Sustainability', code='ENV101', teacher_id=teacher2.id, credits=3),
            Course(section_id=sec5.id, name='Indian Constitution and Democracy', code='POL101', teacher_id=teacher2.id, credits=3),
            Course(section_id=sec5.id, name='Python and Data Structure (LAB)', code='CS102', teacher_id=teacher1.id, credits=4),
        ]
        soai_courses = [
            Course(section_id=sec_soai_1.id, name='DS in C Lab', code='AI101L', teacher_id=greeta.id, credits=2),
            Course(section_id=sec_soai_1.id, name='AI in Programming', code='AI101', teacher_id=greeta.id, credits=4),
            Course(section_id=sec_soai_1.id, name='Critical Thinking', code='HUM101', teacher_id=siddharth.id, credits=3),
            Course(section_id=sec_soai_1.id, name='AI Programming Lab', code='AI102L', teacher_id=greeta.id, credits=2),
            Course(section_id=sec_soai_1.id, name='Intro to Embedded Systems and Robotics', code='AI201', teacher_id=greeta.id, credits=4),
            Course(section_id=sec_soai_1.id, name='Data Structures', code='AI202', teacher_id=greeta.id, credits=4),
            Course(section_id=sec_soai_1.id, name='Indian Constitution', code='POL102', teacher_id=siddanth.id, credits=3),
            Course(section_id=sec_soai_1.id, name='OOP\'s', code='AI203', teacher_id=pankaj.id, credits=4),
            Course(section_id=sec_soai_1.id, name='P&S', code='MATH102', teacher_id=arun_kumar.id, credits=4),
        ]
        db.session.add_all(s1_courses + s2_courses + s3_courses + s4_courses + s5_courses + soai_courses)
        db.session.commit()

        # =====================================================================
        # 6. ENROLLMENTS
        # =====================================================================
        for student, courses in [(harshitha, s2_courses), (riddhima, s2_courses), (vaibhav, s3_courses), 
                                 (sharan, s4_courses), (sadhana, soai_courses), (saiteja, s5_courses), (balaaditya, s1_courses)]:
            for c in courses:
                db.session.add(Enrollment(student_id=student.id, course_id=c.id))
        db.session.commit()

        # =====================================================================
        # 7. TIMETABLE ENTRIES
        # =====================================================================
        sec1_tt = [
            (0, '09:00 AM', '10:30 AM', 'Introduction to Data Structures', 'AB1 - 101', 'var(--success-color)', 'Nitish', 'Period 1'),
            (0, '12:40 PM', '02:05 PM', 'Indian Constitution and Democracy', 'AB2 - 203', '#a78bfa', 'Megha Kapoor', 'Period 2'),
            (0, '02:15 PM', '03:40 PM', 'Environment and Sustainability', 'AB2 - Mini Auditorium', 'var(--warning-color)', 'Gopi', 'Period 3'),
            (1, '09:00 AM', '10:30 AM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)', 'Beaula', 'Period 1'),
            (1, '03:50 PM', '05:15 PM', 'PDS Lab', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)', 'Arjun', 'Period 2'),
            (2, '10:40 AM', '12:10 PM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)', 'Beaula', 'Period 1'),
            (2, '12:40 PM', '02:05 PM', 'Programming in Python', 'AB2 - 207', '#f472b6', 'Arjun', 'Period 2'),
            (2, '02:15 PM', '03:40 PM', 'Environment and Sustainability', 'AB2 - Mini Auditorium', 'var(--warning-color)', 'Gopi', 'Period 3'),
            (3, '10:40 AM', '12:10 PM', 'Introduction to Data Structures', 'AB1 - Moot Court Hall', 'var(--success-color)', 'Nitish', 'Period 1'),
            (3, '12:40 PM', '02:05 PM', 'Indian Constitution and Democracy', 'AB2 - 202', '#a78bfa', 'Megha Kapoor', 'Period 2'),
            (4, '10:40 AM', '12:10 PM', 'Programming in Python', 'AB2 - 203', '#f472b6', 'Arjun', 'Period 1'),
            (4, '02:10 PM', '03:35 PM', 'PDS Lab', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)', 'Arjun', 'Period 2'),
        ]
        
        sec2_tt = [
            (0, '09:00 AM', '10:40 AM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)', 'Sarah Davis', 'Period 1'),
            (0, '10:40 AM', '12:10 PM', 'Indian Constitution and Democracy', 'AB2 - 202', '#a78bfa', 'Sarah Davis', 'Period 2'),
            (0, '02:15 PM', '03:40 PM', 'Environment and Sustainability', 'AB2 - Mini Auditorium', 'var(--warning-color)', 'Sarah Davis', 'Period 3'),
            (1, '09:00 AM', '10:30 AM', 'Programming in Python', 'AB2 - 202', '#f472b6', 'John Smith', 'Period 1'),
            (1, '12:20 PM', '01:40 PM', 'PDS Lab', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)', 'John Smith', 'Period 2'),
            (2, '10:00 AM', '11:30 AM', 'Indian Constitution and Democracy', 'AB2 - 101', '#a78bfa', 'Sarah Davis', 'Period 1'),
            (2, '12:40 PM', '02:05 PM', 'Introduction to Data Structures', 'AB1 - Moot Court Hall', 'var(--success-color)', 'John Smith', 'Period 2'),
            (2, '02:15 PM', '03:40 PM', 'Environment and Sustainability', 'AB2 - Mini Auditorium', 'var(--warning-color)', 'Sarah Davis', 'Period 3'),
            (3, '10:00 AM', '11:30 AM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)', 'Sarah Davis', 'Period 1'),
            (3, '01:40 PM', '03:05 PM', 'Programming in Python', 'AB2 - 101', '#f472b6', 'John Smith', 'Period 2'),
            (4, '10:40 AM', '12:10 PM', 'PDS Lab', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)', 'Arjun', 'Period 1'),
            (4, '12:40 PM', '02:05 PM', 'Introduction to Data Structures', 'AB2 - 202', 'var(--success-color)', 'John Smith', 'Period 2'),
        ]

        sec3_tt = [
            (0, '10:40 AM', '12:10 PM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)', 'Sarah Davis', 'Period 1'),
            (0, '02:15 PM', '03:40 PM', 'Indian Constitution and Democracy', 'AB2 - 202', '#a78bfa', 'Sarah Davis', 'Period 2'),
            (0, '03:50 PM', '05:15 PM', 'PDS Lab', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)', 'John Smith', 'Period 3'),
            (1, '09:00 AM', '10:30 AM', 'Introduction to Data Structures', 'AB1 - 101', 'var(--success-color)', 'John Smith', 'Period 1'),
            (1, '12:15 PM', '01:45 PM', 'Environment and Sustainability', 'AB1 - Moot Court Hall', 'var(--warning-color)', 'Sarah Davis', 'Period 2'),
            (2, '09:00 AM', '10:30 AM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)', 'Sarah Davis', 'Period 1'),
            (2, '02:15 PM', '03:40 PM', 'Indian Constitution and Democracy', 'AB2 - 207', '#a78bfa', 'Sarah Davis', 'Period 2'),
            (3, '09:00 AM', '10:30 AM', 'Programming in Python', 'AB2 - 207', '#f472b6', 'John Smith', 'Period 1'),
            (3, '12:20 PM', '01:40 PM', 'PDS Lab', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)', 'John Smith', 'Period 2'),
            (4, '10:40 AM', '12:10 PM', 'Programming in Python', 'AB2 - 202', '#f472b6', 'John Smith', 'Period 1'),
            (4, '02:15 PM', '03:40 PM', 'Introduction to Data Structures', 'AB2 - 202', 'var(--success-color)', 'John Smith', 'Period 2'),
            (4, '03:50 PM', '05:15 PM', 'Environment and Sustainability', 'AB2 - 202', 'var(--warning-color)', 'Sarah Davis', 'Period 3'),
        ]

        sec4_tt = [
            (0, '09:00 AM', '10:30 AM', 'Indian Constitution and Democracy', 'AB2-202', '#a78bfa', 'Vivek Yadav', 'Period 1'),
            (0, '01:40 PM', '03:05 PM', 'Programming in Python', 'AB2-101', '#f472b6', 'Ujjwal', 'Period 2'),
            (1, '09:00 AM', '10:30 AM', 'Discrete Mathematics', 'AB1-104', 'var(--primary-color)', 'Tamilarasi', 'Period 1'),
            (1, '03:50 PM', '05:15 PM', 'Environment and Sustainability', 'AB2 - 207', 'var(--warning-color)', 'Kishore', 'Period 2'),
            (2, '09:00 AM', '10:30 AM', 'PDS Lab', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)', 'Arjun', 'Period 1'),
            (2, '10:40 AM', '12:10 PM', 'Introduction to Data Structures', 'AB2-202', 'var(--success-color)', 'Vishal', 'Period 2'),
            (2, '01:40 PM', '03:05 PM', 'Programming in Python', 'AB2-203', '#f472b6', 'Ujjwal', 'Period 3'),
            (3, '09:00 AM', '10:30 AM', 'Introduction to Data Structures', 'AB2-101', 'var(--success-color)', 'Vishal', 'Period 1'),
            (3, '10:40 AM', '12:10 PM', 'PDS Lab', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)', 'Arjun', 'Period 2'),
            (3, '12:40 PM', '02:05 PM', 'Indian Constitution and Democracy', 'AB1-104', '#a78bfa', 'Vivek Yadav', 'Period 3'),
            (4, '10:35 AM', '12:05 PM', 'Environment and Sustainability', 'AB2 - 101', 'var(--warning-color)', 'Kishore', 'Period 1'),
            (4, '02:15 PM', '03:40 PM', 'Discrete Mathematics', 'AB2-203', 'var(--primary-color)', 'Tamilarasi', 'Period 2'),
        ]

        sec5_tt = [
            (0, '10:35 AM', '12:05 PM', 'Environment and Sustainability', 'AB1 - 101', 'var(--warning-color)', 'Sarah Davis', 'Period 1'),
            (0, '12:15 PM', '01:45 PM', 'Discrete Mathematics', 'AB1 - 104', 'var(--primary-color)', 'Sarah Davis', 'Period 2'),
            (0, '02:10 PM', '03:35 PM', 'PDS Lab', 'Computer Lab - AB1 - First Floor', 'var(--accent-color)', 'John Smith', 'Period 3'),
            (1, '09:00 AM', '10:30 AM', 'Introduction to Data Structures', 'AB2 - 101', 'var(--success-color)', 'John Smith', 'Period 1'),
            (1, '12:15 PM', '01:45 PM', 'Programming in Python', 'AB1 - 104', '#f472b6', 'John Smith', 'Period 2'),
            (2, '01:40 PM', '03:05 PM', 'Indian Constitution and Democracy', 'AB2 - 202', '#a78bfa', 'Sarah Davis', 'Period 1'),
            (3, '10:35 AM', '12:05 PM', 'Indian Constitution and Democracy', 'AB2 - 202', '#a78bfa', 'Sarah Davis', 'Period 1'),
            (3, '02:15 PM', '03:40 PM', 'Discrete Mathematics', 'AB2 - 203', 'var(--primary-color)', 'Sarah Davis', 'Period 2'),
            (4, '10:40 AM', '12:10 PM', 'Environment and Sustainability', 'AB1 - 104', 'var(--warning-color)', 'Sarah Davis', 'Period 1'),
            (4, '12:15 PM', '01:45 PM', 'Introduction to Data Structures', 'AB2 - 101', 'var(--success-color)', 'John Smith', 'Period 2'),
            (4, '02:15 PM', '03:40 PM', 'Programming in Python', 'AB2 - 101', '#f472b6', 'John Smith', 'Period 3'),
        ]

        for section, tt in [(sec1, sec1_tt), (sec2, sec2_tt), (sec3, sec3_tt), (sec4, sec4_tt), (sec5, sec5_tt)]:
            for day, st, et, title, room, color, teacher, period in tt:
                db.session.add(TimetableEntry(section_id=section.id, day=day, start_time=st, end_time=et, title=title, room=room, color=color, teacher=teacher, period=period))

        db.session.add_all([
            Announcement(school_id=school.id, teacher_id=dean.id, title='Welcome!', body='Classes start March 10.'),
            TeacherTodo(teacher_id=teacher1.id, title='Grade Assignment 1'),
            FriendRequest(sender_id=sharan.id, recipient_id=vaibhav.id, status='accepted'),
            Friendship(user1_id=sharan.id, user2_id=vaibhav.id)
        ])
        db.session.commit()
        
        # =====================================================================
        # 8. FEES
        # =====================================================================
        from app.models import Fee, FeePayment
        
        # Set up a generic fee structure for the batch
        due = datetime(2025, 5, 15)
        students = [vaibhav, sharan, harshitha, riddhima, saiteja, balaaditya, sadhana]
        fees = []
        for s in students:
            fees.append(
                Fee(
                    student_id=s.id,
                    tuition_fee=50000.0,
                    lab_fee=5000.0,
                    library_fee=2000.0,
                    exam_fee=3000.0,
                    other_charges=1000.0,
                    due_date=due
                )
            )
        db.session.add_all(fees)
        db.session.commit()
        
        # Add some mock payments
        payments = [
            FeePayment(fee_id=fees[0].id, amount=61000.0, payment_method='Net Banking', status='success', transaction_id='TXN982374'), # Vaibhav - fully paid
            FeePayment(fee_id=fees[1].id, amount=30000.0, payment_method='UPI', status='success', transaction_id='TXN992834'), # Sharan - partially paid
            FeePayment(fee_id=fees[2].id, amount=61000.0, payment_method='Credit Card', status='success', transaction_id='TXN112233'), # Harshitha - fully paid
        ]
        db.session.add_all(payments)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_db()
