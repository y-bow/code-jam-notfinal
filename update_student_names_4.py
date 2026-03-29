from app import create_app
from app.models import db, User

app = create_app()

def update_names():
    with app.app_context():
        # Map of email to correct name
        corrections = {
            "manastej.p-29@scds.saiuniversity.edu.in": "Patnam Manas Tej"
        }

        updated_count = 0
        for email, correct_name in corrections.items():
            user = User.query.filter_by(email=email).first()
            if user:
                if user.name != correct_name:
                    print(f"Updating {user.email}: '{user.name}' -> '{correct_name}'")
                    user.name = correct_name
                    updated_count += 1
            else:
                print(f"Warning: User with email {email} not found.")

        db.session.commit()
        print(f"Finished. Updated {updated_count} names.")

if __name__ == "__main__":
    update_names()
