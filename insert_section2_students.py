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
        section = Section.query.filter_by(name='Section 2', school_id=school.id).first()
        if not section:
            print("Error: Section 2 not found for SCDS.")
            # Let's check what sections exist
            sections = Section.query.filter_by(school_id=school.id).all()
            print(f"Available sections: {[s.name for s in sections]}")
            return

        print(f"Adding students to {school.name} - {section.name} (ID: {section.id})")

        pw_hash = bcrypt.generate_password_hash("hive@1234").decode('utf-8')

        student_data = [
            ("Mormineni Jishnu Teja", "jishnuteja.m-29@scds.saiuniversity.edu.in"),
            ("Otiddy Sai Praharsa Reddy", "praharsareddy.o-29@scds.saiuniversity.edu.in"),
            ("Kadiveti Niwas", "nivas.k-29@scds.saiuniversity.edu.in"),
            ("Rachuri Harsha Vardhan", "harshavardhan.r-29@scds.saiuniversity.edu.in"),
            ("Polisetty Venkata Surya Jathin", "venkatasuryajathin.p-29@scds.saiuniversity.edu.in"),
            ("Seepareddy Amarnath Reddy", "amarnathreddy.s-29@scds.saiuniversity.edu.in"),
            ("Dirisala Sai Venkata Kartheek", "saivenkatakartheek.d-29@scds.saiuniversity.edu.in"),
            ("Shaik Sadhik", "sadhik.s-29@scds.saiuniversity.edu.in"),
            ("Sakam Mokshitha Reddy", "mokshithareddy.s-29@scds.saiuniversity.edu.in"),
            ("Gampanapalli Karthik", "karthik.g-29@scds.saiuniversity.edu.in"),
            ("Gadipudi Pranathi", "pranathi.g-29@scds.saiuniversity.edu.in"),
            ("Cheppali Ummar Farook", "ummarfarook.c-29@scds.saiuniversity.edu.in"),
            ("Pudota Akhil", "akhil.p-29@scds.saiuniversity.edu.in"),
            ("Vulli Geeta", "geetha.v-29@scds.saiuniversity.edu.in"),
            ("Chaganti Avinash", "avinash.c-29@scds.saiuniversity.edu.in"),
            ("Dasari Sai Sadhvik", "saisadhvik.d-29@scds.saiuniversity.edu.in"),
            ("Dandu Mohith Varma", "mohithvarma.d-29@scds.saiuniversity.edu.in"),
            ("Marrikanti Venkata Dhanush", "venkatadhanush.m-29@scds.saiuniversity.edu.in"),
            ("Angina Pradeep Kumar", "pradeepkumar.a-29@scds.saiuniversity.edu.in"),
            ("Velpula Sai Sravan", "saisravan.v-29@scds.saiuniversity.edu.in"),
            ("Marrigunta Sai Charan", "saicharan.m-29@scds.saiuniversity.edu.in"),
            ("Boddu Mani Sampreeth Reddy", "manisampreeth.b-29@scds.saiuniversity.edu.in"),
            ("Maniswarreddy Boddu", "maniswarreddy.b-29@scds.saiuniversity.edu.in"),
            ("Bodi Hari Babu", "bodihari.b-29@scds.saiuniversity.edu.in"),
            ("Chandra Padmaja", "padmaja.c-29@scds.saiuniversity.edu.in"),
            ("Shaik Khaja Nawaz", "khajanawaz.s-29@scds.saiuniversity.edu.in"),
            ("Shaik Rushma", "rushma.s-29@scds.saiuniversity.edu.in"),
            ("Gangavarapu Pradeep", "pradeep.g-29@scds.saiuniversity.edu.in"),
            ("Rithul S", "rithul.s-29@scds.saiuniversity.edu.in"),
            ("Rudraraju Srikar Siva Phani Padmaraju", "srikarsivaphanipadmaraju.r-29@scds.saiuniversity.edu.in"),
            ("Besta Manasa Udayini", "manasaudayini.b-29@scds.saiuniversity.edu.in"),
            ("Yarramasetti Sai Eswar", "saieswar.y-29@scds.saiuniversity.edu.in"),
            ("Bommanahal Jaswanth Chowdary", "jaswanth.b-29@scds.saiuniversity.edu.in"),
            ("Madala Gopi Chandu", "gopichandu.m-29@scds.saiuniversity.edu.in"),
            ("Vajrala Spandana", "spandana.v-29@scds.saiuniversity.edu.in"),
            ("Pemmasani Dheeraj", "dheeraj.p-29@scds.saiuniversity.edu.in"),
            ("Gundala Venkata Himesh", "venkathimesh.g-29@scds.saiuniversity.edu.in"),
            ("Pemmasani Eswaradesh", "eswardesh.p-29@scds.saiuniversity.edu.in"),
            ("Kommi Harshith", "harshith.k-29@scds.saiuniversity.edu.in"),
            ("Tumu Indra Reddy", "indrareddy.t-29@scds.saiuniversity.edu.in"),
            ("Maddela Nanda Kishore", "nandakishore.m-29@scds.saiuniversity.edu.in"),
            ("Bommaka Harshitha", "harshitha.b-29@scds.saiuniversity.edu.in"),
            ("Pagadala Venkata Prabhu Likith", "prabhulikith.p-29@scds.saiuniversity.edu.in"),
            ("Bombethula Mohan Vamsi Yadav", "mohanvamsiyadav.b-29@scds.saiuniversity.edu.in"),
            ("Turupusima Chavva Harshitha Reddy", "harshithareddy.t-29@scds.saiuniversity.edu.in"),
            ("Sandrapalli Jahnavi", "jahnavi.s-29@scds.saiuniversity.edu.in"),
            ("Banu Prakash Ramapuram", "prakash.b-29@scds.saiuniversity.edu.in"),
            ("Garikipati Akshaya", "akshaya.g-29@scds.saiuniversity.edu.in"),
            ("Chaganti Chennakesava Srikar Reddy", "srikarreddy.c-29@scds.saiuniversity.edu.in"),
            ("Thota Thrishika", "thrishika.t-29@scds.saiuniversity.edu.in"),
            ("Chemudugunta Thanush", "thanush.c-29@scds.saiuniversity.edu.in"),
            ("Balasamudram Sai Charan", "saicharan.b-29@scds.saiuniversity.edu.in"),
            ("Oggu Madhu Priya", "madhupriya.o-29@scds.saiuniversity.edu.in"),
            ("Baddam Ranjith Reddy", "ranjithreddy.b-29@scds.saiuniversity.edu.in"),
            ("Dudekula Thanveer", "thanveer.d-29@scds.saiuniversity.edu.in"),
            ("Dhanyasi Sandesh Joyal", "sandeshjoyal.d-29@scds.saiuniversity.edu.in"),
            ("Maramreddy Sulakshan Reddy", "sulakshanreddy.m-29@scds.saiuniversity.edu.in"),
            ("Singari Dinesh", "dinesh.s-29@scds.saiuniversity.edu.in"),
            ("Yeduru Lavanya", "lavanya.y-29@scds.saiuniversity.edu.in"),
            ("Gutti Jitendra Pavan", "jitendrapavan.g-29@scds.saiuniversity.edu.in"),
            ("Budhala Pardeep", "pardeep.b-29@scds.saiuniversity.edu.in"),
            ("Yeturi Rakesh", "rakesh.y-29@scds.saiuniversity.edu.in"),
            ("Zaahin Bhattacharyya", "zaahin.b-29@scds.saiuniversity.edu.in"),
            ("Pera Charan Kumar Reddy", "charankumarreddy.p-29@scds.saiuniversity.edu.in"),
            ("Padarthi Mohan Sabarish", "mohansabarish.p-29@scds.saiuniversity.edu.in"),
            ("Pikkili Dharma Sai Kumar", "dharmasaikumar.p-29@scds.saiuniversity.edu.in"),
            ("Pasupuleti Mognesh", "mognesh.p-29@scds.saiuniversity.edu.in"),
            ("Chenna Reddy Gari Manoj Reddy", "garimanojreddy.c-29@scds.saiuniversity.edu.in"),
            ("Unnam Manmohan", "manmohan.u-29@scds.saiuniversity.edu.in"),
            ("Edamalakandi Chaturved", "chaturved.e-29@scds.saiuniversity.edu.in"),
            ("Eswar Sangeetha", "sangeetha.e-29@scds.saiuniversity.edu.in"),
            ("Pagadala Riddhima", "ruddhima.p-29@scds.saiuniversity.edu.in"),
            ("Singamala Santhosh Reddy", "santhoshreddy.s-29@scds.saiuniversity.edu.in"),
            ("Koncha Venkata Ravi Teja Reddy", "ravitejareddy.k-29@scds.saiuniversity.edu.in"),
            ("Koncha Pradeep", "pradeep.k-29@scds.saiuniversity.edu.in"),
            ("Iska Sri Charan", "sricharan.i-29@scds.saiuniversity.edu.in"),
            ("Sai Manikanta Vinay Malireddy", "manikantavinay.s-29@scds.saiuniversity.edu.in"),
            ("Jana Phani Kumar", "phanikumar.j-29@scds.saiuniversity.edu.in"),
            ("Gangisetti Vikas Sri Raj", "vikassriraj.g-29@scds.saiuniversity.edu.in"),
            ("Gangisetti Hemanth Sai Krishna", "hemanthsai.g-29@scds.saiuniversity.edu.in"),
            ("Maddirla Manoj Kumar Reddy", "manojkumarreddy.m-29@scds.saiuniversity.edu.in"),
            ("Alahari Venkata Sai Santhosh", "saisanthosh.a-29@scds.saiuniversity.edu.in"),
            ("Mullagoori Arjun", "arjun.m-29@scds.saiuniversity.edu.in"),
            ("Lukkani Deepak", "deepak.l-29@scds.saiuniversity.edu.in"),
            ("Patnaik Manas Tej", "manastej.p-29@scds.saiuniversity.edu.in")
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
