"""
Re-seeds Section 3 students with corrected data from the official spreadsheet.
- Adds lab_section column to students table first (idempotent)
- Clears all seeded Section 3 students (preserves placeholder accounts)
- Re-creates all 85 students with correct names/emails/lab_section tags
- Students 75-85 get lab_section=8 (they will not see the PDS LAB entries)
"""
from app import create_app
from app.models import db, Section, User, Student, bcrypt
import sqlalchemy

app = create_app()

# -----------------------------------------------------------------------
# Rows 1-74: Lab Section 3
# Rows 75-85: Lab Section 8
# Format: (Name, Email, lab_section)
# -----------------------------------------------------------------------
STUDENTS_SECTION_3 = [
    # --- Lab Section 3 ---
    ("Gangapurapu Jai Charan",              "jaicharan.g-29@scds.saiuniversity.edu.in",     3),
    ("Payyavula Shashank",                   "shashank.p-29@scds.saiuniversity.edu.in",       3),
    ("Dondati Pradeep",                      "pradeep.d-29@scds.saiuniversity.edu.in",        3),
    ("G Yoshithaa Sree",                     "yoshithaasree.g-29@scds.saiuniversity.edu.in",  3),
    ("Konapalli Poojitha",                   "poojitha.k-29@scds.saiuniversity.edu.in",       3),
    ("Mandem Sai Vani",                      "saivani.m-29@scds.saiuniversity.edu.in",        3),
    ("Thirividhi Jaswanth",                  "jaswanth.t-29@scds.saiuniversity.edu.in",       3),
    ("Chennuru Veera Manjunatha Reddy",      "manjunathareddy.c-29@scds.saiuniversity.edu.in",3),
    ("Kajjayam Sai Mourya",                  "saimourya.k-29@scds.saiuniversity.edu.in",      3),
    ("Mekala Navya Sri",                     "navyasri.m-29@scds.saiuniversity.edu.in",       3),
    ("Kattamreddy Lakshmi Chaitra",          "lakshmichaitra.k-29@scds.saiuniversity.edu.in", 3),
    ("Chanduluru Sanhitha Yadav",            "sanhithayadav.c-29@scds.saiuniversity.edu.in",  3),
    ("Malli Divya",                          "divya.m-29@scds.saiuniversity.edu.in",          3),
    ("Dondati Pavitra",                      "pavitra.d-29@scds.saiuniversity.edu.in",        3),
    ("Ramireddy Siva Likitha Reddy",         "sivalikitha.r-29@scds.saiuniversity.edu.in",    3),
    ("Udatha Sri Vennela",                   "srivennela.u-29@scds.saiuniversity.edu.in",     3),
    ("Vagathuri Bhargava",                   "bhargava.v-29@scds.saiuniversity.edu.in",       3),
    ("Valapalli Ram Teja",                   "ramteja.v-29@scds.saiuniversity.edu.in",        3),
    ("Kamireddy Yoshith Reddy",              "yoshithreddy.k-29@scds.saiuniversity.edu.in",   3),
    ("Peddireddy Sai Darshan Reddy",         "saidarshanreddy.p-29@scds.saiuniversity.edu.in",3),
    ("Innamuri Venkata Sai Lohith",          "venkatasai.i-29@scds.saiuniversity.edu.in",     3),
    ("Myla Pavan",                           "pavan.m-29@scds.saiuniversity.edu.in",          3),
    ("Duvvuru Deepak Reddy",                 "deepakreddy.d-29@scds.saiuniversity.edu.in",    3),
    ("P Tharun",                             "tharun.p-29@scds.saiuniversity.edu.in",         3),
    ("Pramidhala Hemanth",                   "hemanth.p-29@scds.saiuniversity.edu.in",        3),
    ("Marri Bhanu Sri",                      "bhanusri.m-29@scds.saiuniversity.edu.in",       3),
    ("Yelluri Harshavardhan Reddy",          "harshavardhanreddy.y-29@scds.saiuniversity.edu.in", 3),
    ("Rachavelpula Puneeth Sai",             "puneethsai.r-29@scds.saiuniversity.edu.in",     3),
    ("Siginam Sai Sathwik",                  "saisathwik.s-29@scds.saiuniversity.edu.in",     3),
    ("Palacharla Vamsi Krishna",             "vamsikrishna.p-29@scds.saiuniversity.edu.in",   3),
    ("Amarthaluru Bhavesh",                  "bhavesh.a-29@scds.saiuniversity.edu.in",        3),
    ("Telaganeni Lohith Manish",             "lohithmanish.t-29@scds.saiuniversity.edu.in",   3),
    ("Bangarugari Prathyush",                "prathyush.b-29@scds.saiuniversity.edu.in",      3),
    ("Mahasamudhram Girish Reddy",           "girishreddy.m-29@scds.saiuniversity.edu.in",    3),
    ("Golla Siva Tharun",                    "sivatharun.g-29@scds.saiuniversity.edu.in",     3),
    ("Manupati Poorna Chandra",              "poornaachandra.m-29@scds.saiuniversity.edu.in", 3),
    ("Rathinakumar S",                       "rathinakumar.s-29@scds.saiuniversity.edu.in",   3),
    ("Godduvelagala Chennakesava",           "chennakesava.g-29@scds.saiuniversity.edu.in",   3),
    ("Advait D",                             "advait.d-29@scds.saiuniversity.edu.in",         3),
    ("Yelchuri Ganesh",                      "ganesh.y-29@scds.saiuniversity.edu.in",         3),
    ("Dondlapadu Ramya Sree",                "ramyasree.d-29@scds.saiuniversity.edu.in",      3),
    ("Panyam Venkata Gyana Deepak",          "gyanadeepak.p-29@scds.saiuniversity.edu.in",    3),
    ("Ilupuru Padmajahnavi",                 "padmajahnavi.i-29@scds.saiuniversity.edu.in",   3),
    ("Malchi Sneha Sruthi",                  "snehasruthi.m-29@scds.saiuniversity.edu.in",    3),
    ("Devarinti Suma Sri",                   "sumasri.d-29@scds.saiuniversity.edu.in",        3),
    ("Badhvel Hansika Srinidhi",             "hansikasrinidhi.b-29@scds.saiuniversity.edu.in",3),
    ("Pichika V Vyshnavi",                   "vyshnavi.p-29@scds.saiuniversity.edu.in",       3),
    ("Kannikapuram Teja",                    "teja.k-29@scds.saiuniversity.edu.in",           3),
    ("Chinka Sumanth",                       "sumanth.c-29@scds.saiuniversity.edu.in",        3),
    ("Arkadu Mokshitha",                     "mokshitha.a-29@scds.saiuniversity.edu.in",      3),
    ("Gajji Bhargavi",                       "bhargavi.g-29@scds.saiuniversity.edu.in",       3),
    ("Chagam Riteeswar Reddy",               "riteeswar.c-29@scds.saiuniversity.edu.in",      3),
    ("Kotagasti Taheer",                     "thaheer.k-29@scds.saiuniversity.edu.in",        3),
    ("Peravali Puvan Venkata Pavan",         "venkatapavan.p-29@scds.saiuniversity.edu.in",   3),
    ("Bathula Hanuma Kotireddy",             "hanumakotireddy.b-29@scds.saiuniversity.edu.in",3),
    ("Yenneti Gowtham Sri Sai Srinivasa Murthy", "gowthamsri.y-29@scds.saiuniversity.edu.in",3),
    ("Ramireddy Bhavadeep Reddy",            "bhavadeepreddy.r-29@scds.saiuniversity.edu.in", 3),
    ("Palisetti Harsha Deepika",             "deepikaharsha.p-29@scds.saiuniversity.edu.in",  3),
    ("Purini Tejeswar",                      "tejeswar.p-29@scds.saiuniversity.edu.in",       3),
    ("Nagireddy Naveen",                     "naveen.n-29@scds.saiuniversity.edu.in",         3),
    ("Vunnam Kowshik",                       "kowshik.v-29@scds.saiuniversity.edu.in",        3),
    ("Palleboyina Vamsi Krishna",            "vamsikrishna.pl-29@scds.saiuniversity.edu.in",  3),
    ("Venna Bhuvaneshwar",                   "bhuvaneshwar.v-29@scds.saiuniversity.edu.in",   3),
    ("Kilari Hithesh",                       "kilari.h-29@scds.saiuniversity.edu.in",         3),
    ("Boddu Vamsidhar Reddy",                "vamsidharreddy.b-29@scds.saiuniversity.edu.in", 3),
    ("Anbuchelvan V",                        "anbuchelvan.v-29@scds.saiuniversity.edu.in",    3),
    ("B Vaibhav",                            "vaibhav.b-29@scds.saiuniversity.edu.in",        3),
    ("S T Suneethra",                        "suneethra.s-29@scds.saiuniversity.edu.in",      3),
    ("Kolamasanapalli Manjunath",            "manjunath.k-29@scds.saiuniversity.edu.in",      3),
    ("Dhanemkula Veera Bhargav",             "veerabhargav.d-29@scds.saiuniversity.edu.in",   3),
    ("Ontimitta Keerthana",                  "keerthana.o-29@scds.saiuniversity.edu.in",      3),
    ("Koneru Haneeth",                       "haneeth.k-29@scds.saiuniversity.edu.in",        3),
    ("Golla Shiva Santhosh Reddy",           "shivasanthoshreddy.g-29@scds.saiuniversity.edu.in", 3),
    ("Vudata Sri Madhavan",                  "srimadhavan.v-29@scds.saiuniversity.edu.in",    3),
    # --- Lab Section 8 ---
    ("Dudi Venkata Krishna Karthik",         "venkatakrishnakarthik.d-29@scds.saiuniversity.edu.in", 8),
    ("Thati Sushmanth Reddy",                "sushmanthreddy.t-29@scds.saiuniversity.edu.in", 8),
    ("Mallela Mohammad Aqib",                "mohammadaqib.m-29@scds.saiuniversity.edu.in",   8),
    ("M Arun Kumar",                         "arunkumar.m-29@scds.saiuniversity.edu.in",      8),
    ("Dasari Venkata Yeswanth",              "venkatayaswanth.d-29@scds.saiuniversity.edu.in",8),
    ("Boddu Chiranjeevi",                    "chiranjeevi.b-29@scds.saiuniversity.edu.in",     8),
    ("Gurram Mahesh",                        "mahesh.g-29@scds.saiuniversity.edu.in",         8),
    ("Ganugapenta Naga Mahesh",              "nagamahesh.g-29@scds.saiuniversity.edu.in",      8),
    ("Beeram Naga Maheswar Reddy",           "maheswar.b-29@scds.saiuniversity.edu.in",       8),
    ("Ayindla Surya",                        "surya.a-29@scds.saiuniversity.edu.in",          8),
    ("Narbavee V",                           "narbavee.v-29@scds.saiuniversity.edu.in",       8),
]

PLACEHOLDER_EMAILS = {
    "superadmin@saiuniversity.edu.in",
    "admin@saiuniversity.edu.in",
    "dean@scds.saiuniversity.edu.in",
    "professor@scds.saiuniversity.edu.in",
    "assistant@scds.saiuniversity.edu.in",
    "rep@scds.saiuniversity.edu.in",
}


def ensure_lab_section_column():
    """Add lab_section column to students table if it doesn't exist (SQLite-safe)."""
    with app.app_context():
        try:
            db.session.execute(db.text(
                "ALTER TABLE students ADD COLUMN lab_section INTEGER"
            ))
            db.session.commit()
            print("Added lab_section column to students table.")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("lab_section column already exists, skipping.")
            else:
                print(f"Column migration note: {e}")


def reseed_section3():
    with app.app_context():
        section = Section.query.filter_by(code='SCDS-CS-S3').first()
        if not section:
            print("ERROR: Section SCDS-CS-S3 not found.")
            return

        school_id = section.school_id
        pw_hash = bcrypt.generate_password_hash("hive@1234").decode('utf-8')

        # Build set of all target emails (authoritative list)
        target_emails = {email for _, email, _ in STUDENTS_SECTION_3}

        # 1. Remove stale seeded users (not in authoritative list, not placeholder)
        existing_students = Student.query.filter_by(section_id=section.id).all()
        removed = 0
        for sp in existing_students:
            user = User.query.get(sp.user_id)
            if user and user.email not in target_emails and user.email not in PLACEHOLDER_EMAILS:
                db.session.delete(sp)
                db.session.delete(user)
                removed += 1
                print(f"REMOVED stale: {user.name} ({user.email})")

        db.session.commit()
        print(f"Removed {removed} stale students.")

        # 2. Upsert all authoritative students
        added = 0
        updated = 0
        skipped = 0

        for name, email, lab_sec in STUDENTS_SECTION_3:
            existing_user = User.query.filter_by(email=email, school_id=school_id).first()

            if existing_user:
                # Update name if different
                if existing_user.name != name:
                    existing_user.name = name

                sp = Student.query.filter_by(user_id=existing_user.id).first()
                if sp:
                    sp.section_id = section.id
                    sp.lab_section = lab_sec
                    sp.enrollment_year = 2025
                    sp.major = "Computer Science"
                    updated += 1
                    print(f"UPDATED: {name} (lab={lab_sec})")
                else:
                    sp = Student(
                        user_id=existing_user.id,
                        section_id=section.id,
                        enrollment_year=2025,
                        major="Computer Science",
                        lab_section=lab_sec
                    )
                    db.session.add(sp)
                    updated += 1
                    print(f"PROFILE ADDED: {name}")
            else:
                user = User(
                    school_id=school_id,
                    email=email,
                    password_hash=pw_hash,
                    role='student',
                    name=name,
                    must_change_password=True
                )
                db.session.add(user)
                db.session.flush()

                sp = Student(
                    user_id=user.id,
                    section_id=section.id,
                    enrollment_year=2025,
                    major="Computer Science",
                    lab_section=lab_sec
                )
                db.session.add(sp)
                added += 1
                print(f"ADDED: {name} ({email}) [lab={lab_sec}]")

        db.session.commit()
        print(f"\nDone! Added: {added}  Updated/Fixed: {updated}  Removed stale: {removed}")
        print(f"Total Section 3 students: {len(STUDENTS_SECTION_3)}")


if __name__ == "__main__":
    ensure_lab_section_column()
    reseed_section3()
