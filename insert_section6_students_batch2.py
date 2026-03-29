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
            ("Netibottu Shaik Mahammad Hujefa", "mahammadhujefa.n-29@scds.saiuniversity.edu.in"),
            ("Nodagala Devarshini Lakshmi Akshaya", "devarshinilakshmiakshaya.n-29@scds.saiuniversity.edu.in"),
            ("Malli Lakshman", "lakshman.m-29@scds.saiuniversity.edu.in"),
            ("Nakka Parimala", "parimala.n-29@scds.saiuniversity.edu.in"),
            ("Bakka Mohith Venkata Ganesh Reddy", "ganeshreddy.b-29@scds.saiuniversity.edu.in"),
            ("Jorige Kalyan Ram", "kalyanram.j-29@scds.saiuniversity.edu.in"),
            ("Maramreddy Shiva Nandheswara Reddy", "shivanandheswarareddy.m-29@scds.saiuniversity.edu.in"),
            ("Sura Bhavana", "bhavana.s-29@scds.saiuniversity.edu.in"),
            ("Nare Sandhya", "sandhya.n-29@scds.saiuniversity.edu.in"),
            ("Chinna Nagappagari Mounika", "mounika.c-29@scds.saiuniversity.edu.in"),
            ("Padarthi Sahithi", "sahithi.p-29@scds.saiuniversity.edu.in"),
            ("Baira Spoorthi", "spoorthi.b-29@scds.saiuniversity.edu.in"),
            ("Malireddy Mineesh", "mineesh.m-29@scds.saiuniversity.edu.in"),
            ("Boodati Jayanth", "jayanth.b-29@scds.saiuniversity.edu.in"),
            ("Palagiri Jeswith Venkata Sai", "jeswithvenkatasai.p-29@scds.saiuniversity.edu.in"),
            ("Tippuluri Safiya", "safiya.t-29@scds.saiuniversity.edu.in"),
            ("Madarapu Jaswanth", "jaswanth.m-29@scds.saiuniversity.edu.in"),
            ("Baddigam Venkateswara Reddy", "venkateswarareddy.b-29@scds.saiuniversity.edu.in"),
            ("Dandela Sri Charan Kumar Reddy", "charankumar.d-29@scds.saiuniversity.edu.in"),
            ("Anamala Hemanth Kumar", "hemanthkumar.a-29@scds.saiuniversity.edu.in"),
            ("Katha Venkata Nishanth Reddy", "venkatanishanthreddy.k-29@scds.saiuniversity.edu.in"),
            ("Santimalla Nihitha", "nihitha.s-29@scds.saiuniversity.edu.in"),
            ("Thalliboyina Sashank", "sashank.t-29@scds.saiuniversity.edu.in"),
            ("Pabolu Vyshnavi Anantha Lakshmi", "vyshnaviananthalakshmi.p-29@scds.saiuniversity.edu.in"),
            ("Gummalla Venkata Santosh Reddy", "santhoshreddy.g-29@scds.saiuniversity.edu.in"),
            ("Sangala Sai Teja", "saiteja.s-29@scds.saiuniversity.edu.in"),
            ("Koppula Venkata Sai Kishore", "venkatasaikishore.k-29@scds.saiuniversity.edu.in"),
            ("Byrugani Ragavarshini", "ragavarshini.b-29@scds.saiuniversity.edu.in"),
            ("Janga Muni Bhargav Reddy", "bhargavreddy.j-29@scds.saiuniversity.edu.in"),
            ("Podalakuru Bindu Lovely", "bindulovely.p-29@scds.saiuniversity.edu.in")
        ]

        added_count = 0
        existing_count = 0

        for name, email in student_data:
            existing = User.query.filter_by(email=email).first()
            if existing:
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
        print(f"Finished. Added: {added_count}, Already existed: {existing_count}")

if __name__ == "__main__":
    insert_students()
