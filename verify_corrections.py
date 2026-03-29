from app import create_app
from app.models import db, User

def verify_corrections():
    app = create_app()
    with app.app_context():
        # Check specific corrections
        checks = [
            'balaaditya.t-29@scds.saiuniversity.edu.in',
            'shilpasatish.s-29@scds.saiuniversity.edu.in',
            'sreesaitanay.a-29@scds.saiuniversity.edu.in',
            'sandhya.a-29@scds.saiuniversity.edu.in',
            'hemasree.r-29@scds.saiuniversity.edu.in'
        ]

        print("Verifying corrections:")
        for email in checks:
            user = User.query.filter_by(email=email).first()
            if user:
                print(f"Correct: {user.email}: {user.name}")
            else:
                print(f"Error: {email}: Not found")

if __name__ == "__main__":
    verify_corrections()
