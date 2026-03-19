import unittest
from app import create_app
from app.models import db, User, LostFoundItem, Message

class LostFoundTestCase(unittest.TestCase):
    def setUp(self):
        import os
        os.environ['DATABASE_URL'] = 'sqlite://'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            from app.models import School
            # Create a mock school
            s = School(name="Test School", code="TS01", domain="test.edu")
            db.session.add(s)
            
            # Create two test users
            u1 = User(email="u1@test.edu", password_hash="hash1", role="student", name="User One", school_id=1)
            u2 = User(email="u2@test.edu", password_hash="hash2", role="student", name="User Two", school_id=1)
            db.session.add_all([u1, u2])
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, email):
        user = User.query.filter_by(email=email).first()
        with self.client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['role'] = user.role

    def test_gallery_access_no_login(self):
        res = self.client.get('/lost-found/gallery', follow_redirects=True)
        self.assertIn(b'Please log in', res.data)

    def test_report_item_and_matching(self):
        with self.app.app_context():
            self.login('u1@test.edu')
            # U1 reports a lost item
            res1 = self.client.post('/lost-found/report', data=dict(
                report_type='lost',
                category='Electronics',
                title='Airpods Pro',
                description='White case, missing right pod.',
                location='Library'
            ), follow_redirects=True)
            self.assertIn(b'Lost item reported successfully', res1.data)
            
            self.login('u2@test.edu')
            # U2 reports a found item matching U1
            res2 = self.client.post('/lost-found/report', data=dict(
                report_type='found',
                category='Electronics',
                title='Airpods Pro',
                description='White case, missing right pod.',
                location='Cafeteria'
            ), follow_redirects=True)
            
            self.assertIn(b'We notified a user whose lost item matches your description', res2.data)
            
            # Verify U1 got a message
            u1 = User.query.filter_by(email="u1@test.edu").first()
            msg = Message.query.filter_by(recipient_id=u1.id).first()
            self.assertIsNotNone(msg)
            self.assertIn('might match your lost item', msg.body)

if __name__ == '__main__':
    unittest.main()
