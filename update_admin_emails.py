from app import create_app
from app.models import db, User

app = create_app()

EMAIL_UPDATES = {
    "superadmin@hive.lms": "superadmin@saiuniversity.edu.in",
    "admin@hive.lms":      "admin@saiuniversity.edu.in",
}

def update_emails():
    with app.app_context():
        for old_email, new_email in EMAIL_UPDATES.items():
            user = User.query.filter_by(email=old_email).first()
            if user:
                user.email = new_email
                print(f"UPDATED: {old_email} -> {new_email}")
            else:
                print(f"NOT FOUND: {old_email}")
        db.session.commit()
        print("Done.")

if __name__ == "__main__":
    update_emails()
