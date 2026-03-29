from app import create_app
from app.models import db, Section, School

app = create_app()

def check_sections():
    with app.app_context():
        school = School.query.filter_by(code='SCDS').first()
        if not school:
            print("School SCDS not found")
            return
            
        sections = Section.query.filter_by(school_id=school.id).all()
        for s in sections:
            print(f"ID: {s.id}, Name: {s.name}, Code: {s.code}")

if __name__ == "__main__":
    check_sections()
