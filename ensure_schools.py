from app import create_app
from app.models import db, School

app = create_app()

def ensure_schools():
    with app.app_context():
        schools_data = [
            ("School of Arts and Sciences", "SAS", "sas.saiuniversity.edu.in"),
            ("School of Computing and Data Science", "SCDS", "scds.saiuniversity.edu.in"),
            ("School of Law", "SOL", "sol.saiuniversity.edu.in"),
            ("School of Artificial Intelligence", "SOAI", "soai.saiuniversity.edu.in"),
            ("School of Media", "SOM", "som.saiuniversity.edu.in"),
            ("School of Technology", "SOT", "sot.saiuniversity.edu.in"),
            ("School of Business", "SOB", "sob.saiuniversity.edu.in"),
            ("School of Allied Health Sciences", "SAHS", "sahs.saiuniversity.edu.in"),
        ]
        
        for name, code, domain in schools_data:
            existing = School.query.filter_by(code=code).first()
            if not existing:
                school = School(name=name, code=code, domain=domain)
                db.session.add(school)
                print(f"Created school {name}")
            else:
                print(f"School {name} already exists")
        
        db.session.commit()

if __name__ == "__main__":
    ensure_schools()
