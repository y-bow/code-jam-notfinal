from app import create_app
from app.models import db, User

def verify_corrections_batch2():
    app = create_app()
    with app.app_context():
        # Check specific correction for batch 2
        email = 'lasyaganapriya.k-29@scds.saiuniversity.edu.in'
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"Correct: {user.email}: {user.name}")
        else:
            print(f"Error: {email}: Not found")

if __name__ == "__main__":
    verify_corrections_batch2()
