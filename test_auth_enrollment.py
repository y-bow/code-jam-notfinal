import unittest
from app import create_app
from app.models import db, User, School, Section, Course, JoinCode, Enrollment, bcrypt
from datetime import datetime, timedelta

class AuthEnrollmentTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # Setup initial data
            s1 = School(name="University A", code="UNIA", domain="uni-a.edu", is_active=True)
            s2 = School(name="University B", code="UNIB", domain="uni-b.edu", is_active=False)
            db.session.add_all([s1, s2])
            db.session.commit()
            
            sec1 = Section(name="CS-A", code="CSA", school_id=s1.id, batch_year=2024)
            db.session.add(sec1)
            db.session.commit()

            valid_hash = bcrypt.generate_password_hash('correct').decode('utf-8')
            t1 = User(name="Prof A", email="prof@uni-a.edu", password_hash=valid_hash, role="professor", school_id=s1.id)
            db.session.add(t1)
            db.session.commit()

            c1 = Course(name="Python 101", code="PY101", section_id=sec1.id, teacher_id=t1.id, credits=3)
            db.session.add(c1)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_registration_domain_matching(self):
        # Valid domain
        response = self.client.post('/register', data={
            'name': 'Student A',
            'email': 'student@uni-a.edu',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }, follow_redirects=True)
        self.assertIn(b'Successfully registered', response.data)
        
        # Invalid domain
        response = self.client.post('/register', data={
            'name': 'Student B',
            'email': 'student@gmail.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }, follow_redirects=True)
        self.assertIn(b'email domain is not registered', response.data)

    def test_login_suspension_checks(self):
        with self.app.app_context():
            valid_hash = bcrypt.generate_password_hash('correct').decode('utf-8')
            u = User(name='Suspended', email='suspended@uni-a.edu', password_hash=valid_hash, role='student', school_id=1, is_suspended=True)
            db.session.add(u)
            db.session.commit()
            
        # Suspended user
        response = self.client.post('/login', data={
            'email': 'suspended@uni-a.edu',
            'password': 'correct'
        }, follow_redirects=True)
        self.assertIn(b'account is currently suspended', response.data)

    def test_join_code_validation(self):
        with self.app.app_context():
            # Create user and code
            valid_hash = bcrypt.generate_password_hash('correct').decode('utf-8')
            u = User(name='Test User', email='test@uni-a.edu', password_hash=valid_hash, role='student', school_id=1)
            db.session.add(u)
            jc = JoinCode(code='TEST12', course_id=1, school_id=1, is_active=True, 
                          expires_at=datetime.utcnow() + timedelta(days=1), max_uses=10)
            db.session.add(jc)
            db.session.commit()
            uid = u.id

        with self.client.session_transaction() as sess:
            sess['user_id'] = uid
            sess['school_id'] = 1
            sess['role'] = 'student'
            sess['name'] = 'Test User'

        # Success join
        response = self.client.post('/classroom/join', data={'code': 'TEST12'}, follow_redirects=True)
        self.assertIn(b'Successfully joined', response.data)

        # Expired code
        with self.app.app_context():
            jc = JoinCode.query.filter_by(code='TEST12').first()
            jc.expires_at = datetime.utcnow() - timedelta(days=1)
            db.session.commit()
        
        response = self.client.post('/classroom/join', data={'code': 'TEST12'}, follow_redirects=True)
        self.assertIn(b'Invalid or expired code', response.data)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AuthEnrollmentTestCase)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        exit(1)
