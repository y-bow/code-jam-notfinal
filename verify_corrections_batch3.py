from app import create_app
from app.models import db, User

def verify_corrections_batch3():
    app = create_app()
    with app.app_context():
        # Check specific corrections for batch 3
        checks = [
            'prasanthsai.b-29@scds.saiuniversity.edu.in',
            'mokshagnarao.p-29@scds.saiuniversity.edu.in',
            'maheshreddy.m-29@scds.saiuniversity.edu.in'
        ]

        print("Verifying corrections for batch 3:")
        for email in checks:
            user = User.query.filter_by(email=email).first()
            if user:
                print(f"Correct: {user.email}: {user.name}")
            else:
                print(f"Error: {email}: Not found")

if __name__ == "__main__":
    verify_corrections_batch3()
