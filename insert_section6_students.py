import os
from app import create_app
from app.models import db, School, Section, User, Student, bcrypt

app = create_app()

def insert_students():
    with app.app_context():
        # Find the School
        school = School.query.filter_by(code='SCDS').first()
        if not school:
            print("Error: School SCDS not found.")
            return

        # Find the Section
        section = Section.query.filter_by(name='Section 6', school_id=school.id).first()
        if not section:
            print("Error: Section 6 not found.")
            return

        print(f"Adding students to {school.name} - {section.name} (ID: {section.id})")

        pw_hash = bcrypt.generate_password_hash("hive@1234").decode('utf-8')

        student_data = [
            ("Doggireddy Saiharshith Reddy", "saiharshithreddy.d-29@scds.saiuniversity.edu.in"),
            ("Palli Keerthana", "keerthana.p-29@scds.saiuniversity.edu.in"),
            ("Gundra Sweenija Reddy", "sweenijareddy.g-29@scds.saiuniversity.edu.in"),
            ("Padarthi Vishnu Vardhan Reddy", "vishnuvardhanreddy.p-29@scds.saiuniversity.edu.in"),
            ("Pannem Uday Kumar", "udaykumar.p-29@scds.saiuniversity.edu.in"),
            ("Maddala Mahesh Kumar Reddy", "maheshkumarreddy.m-29@scds.saiuniversity.edu.in"),
            ("Kavali Madhu Sekhar Reddy", "madhusekharreddy.k-29@scds.saiuniversity.edu.in"),
            ("Thudimella Venkata Likith", "venkatalikith.t-29@scds.saiuniversity.edu.in"),
            ("Thiruvathuru Harsha Vardhan Rayulu", "harshavardhan.t-29@scds.saiuniversity.edu.in"),
            ("Kolli Jeshvitha Reddy", "jeshvithreddy.k-29@scds.saiuniversity.edu.in"),
            ("Syed Sameer Ahamed", "sameerahamed.s-29@scds.saiuniversity.edu.in"),
            ("Buchupalle Siva Mohan Reddy", "sivamohanreddy.b-29@scds.saiuniversity.edu.in"),
            ("Yanamala Goutham Reddy", "gowthamreddy.y-29@scds.saiuniversity.edu.in"),
            ("Bochhu Nitya Sri", "nityasri.b-29@scds.saiuniversity.edu.in"),
            ("Padarthi Thrigun Surya Saran Sreekar", "suryasaransreekar.p-29@scds.saiuniversity.edu.in"),
            ("Veduruparthi Satya Bhaskara Varun", "satyabhaskaravarun.v-29@scds.saiuniversity.edu.in"),
            ("Mahidhar Naidu Kommi", "mahidhar.k-29@scds.saiuniversity.edu.in"),
            ("Dandamudi Rama Nikhita", "ramnikhita.d-29@scds.saiuniversity.edu.in"),
            ("Tulluri Navadeep", "navadeep.t-29@scds.saiuniversity.edu.in"),
            ("Jakkireddy Syam Sundar Pavan Kumar Reddy", "syamsundhar.j-29@scds.saiuniversity.edu.in"),
            ("Lukkani Dheeraj", "dheeraj.l-29@scds.saiuniversity.edu.in"),
            ("Edara Yashwanth Chowdary", "yashwanthchowdary.e-29@scds.saiuniversity.edu.in"),
            ("Mettukuru Santhosh Reddy", "santhoshreddy.m-29@scds.saiuniversity.edu.in"),
            ("Lakku Venkateswarlu", "venkateswarlu.l-29@scds.saiuniversity.edu.in"),
            ("Pulipati Gowtham", "gowtham.p-29@scds.saiuniversity.edu.in"),
            ("Tallu Venkata Mohan Reddy", "mohanreddy.t-29@scds.saiuniversity.edu.in"),
            ("Nellore Sanjana", "sanjana.n-29@scds.saiuniversity.edu.in"),
            ("Yeddula Manoj Kumar Reddy", "manojkumarreddy.y-29@scds.saiuniversity.edu.in"),
            ("M Sai Charan", "saicharan.m2-29@scds.saiuniversity.edu.in")
        ]

        added_count = 0
        existing_count = 0

        for name, email in student_data:
            existing = User.query.filter_by(email=email).first()
            if existing:
                # Update existing student's section if necessary
                student_profile = Student.query.get(existing.id)
                if student_profile:
                    if student_profile.section_id != section.id:
                        print(f"Moving {existing.email} to {section.name}")
                        student_profile.section_id = section.id
                        existing_count += 1
                continue

            user = User(
                school_id=school.id,
                email=email,
                password_hash=pw_hash,
                role='student',
                name=name
            )
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id,
                section_id=section.id,
                enrollment_year=2025,
                major="Computer Science"
            )
            db.session.add(student)
            added_count += 1

        db.session.commit()
        print(f"Finished. Added: {added_count}, Updated/Existed: {existing_count}")

if __name__ == "__main__":
    insert_students()
