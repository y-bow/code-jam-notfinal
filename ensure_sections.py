from app import create_app
from app.models import db, School, Section

app = create_app()

def ensure_sections():
    with app.app_context():
        school = School.query.filter_by(code='SCDS').first()
        if not school:
            print("School SCDS not found")
            return
            
        for i in range(1, 8):
            name = f"Section {i}"
            code = f"SCDS-CS-S{i}"
            existing = Section.query.filter_by(code=code, school_id=school.id).first()
            if not existing:
                section = Section(
                    school_id=school.id,
                    name=name,
                    code=code,
                    batch_year=2025
                )
                db.session.add(section)
                print(f"Created {name}")
            else:
                print(f"{name} already exists")
        
        db.session.commit()

if __name__ == "__main__":
    ensure_sections()
