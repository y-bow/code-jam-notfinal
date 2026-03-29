from app import create_app
from app.models import db, School

app = create_app()

def list_schools():
    with app.app_context():
        schools = School.query.all()
        for s in schools:
            print(f"ID: {s.id}, Name: {s.name}, Code: {s.code}")

if __name__ == "__main__":
    list_schools()
