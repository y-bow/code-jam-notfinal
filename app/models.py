from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

# =============================================================================
# ROLE HIERARCHY
# =============================================================================
ROLE_HIERARCHY = {
    'student': 0,
    'class_rep': 1,
    'teacher': 2,
    'assistant': 3,
    'timetable_manager': 4,
    'dean': 5,
    'admin': 10,
    'superadmin': 99,
}

VALID_ROLES = set(ROLE_HIERARCHY.keys())


# =============================================================================
# TENANT MODELS
# =============================================================================

class School(db.Model):
    """Top-level tenant. All data is isolated per school."""
    __tablename__ = 'schools'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    domain = db.Column(db.String(100))  # e.g. 'scds.saiuniversity.edu.in'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sections = db.relationship('Section', backref='school', lazy='dynamic',
                               cascade='all, delete-orphan')
    users = db.relationship('User', backref='school', lazy='dynamic',
                            cascade='all, delete-orphan')
    announcements = db.relationship('Announcement', backref='school', lazy='dynamic',
                                    cascade='all, delete-orphan')

    def __repr__(self):
        return f'<School {self.code}: {self.name}>'


class Section(db.Model):
    """A section/batch within a school. Courses and students belong to sections."""
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    batch_year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('school_id', 'code', name='uq_section_school_code'),
        db.Index('ix_section_school', 'school_id'),
    )

    # Relationships
    courses = db.relationship('Course', backref='section', lazy='dynamic',
                              cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Section {self.code} @ School {self.school_id}>'


# =============================================================================
# USER MODELS
# =============================================================================

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('school_id', 'email', name='uq_user_school_email'),
        db.Index('ix_user_school', 'school_id'),
        db.Index('ix_user_role', 'school_id', 'role'),
    )

    @property
    def role_level(self):
        return ROLE_HIERARCHY.get(self.role, -1)

    def has_minimum_role(self, min_role):
        return self.role_level >= ROLE_HIERARCHY.get(min_role, 999)

    def __repr__(self):
        return f'<User {self.email} ({self.role}) @ School {self.school_id}>'

    # Social Features
    @property
    def friends(self):
        """Returns a list of User objects who are confirmed friends."""
        f1 = Friendship.query.filter_by(user1_id=self.id).all()
        f2 = Friendship.query.filter_by(user2_id=self.id).all()
        friend_ids = [f.user2_id for f in f1] + [f.user1_id for f in f2]
        if not friend_ids:
            return []
        return User.query.filter(User.id.in_(friend_ids)).all()

    @property
    def pending_requests(self):
        """Incoming friend requests."""
        return FriendRequest.query.filter_by(recipient_id=self.id, status='pending').all()

    @property
    def sent_requests(self):
        """Outgoing friend requests."""
        return FriendRequest.query.filter_by(sender_id=self.id, status='pending').all()

    def is_friends_with(self, other_user_id):
        return Friendship.query.filter(
            ((Friendship.user1_id == self.id) & (Friendship.user2_id == other_user_id)) |
            ((Friendship.user1_id == other_user_id) & (Friendship.user2_id == self.id))
        ).first() is not None

    def has_pending_request_to(self, other_user_id):
        return FriendRequest.query.filter_by(
            sender_id=self.id, recipient_id=other_user_id, status='pending'
        ).first() is not None

    def has_pending_request_from(self, other_user_id):
        return FriendRequest.query.filter_by(
            sender_id=other_user_id, recipient_id=self.id, status='pending'
        ).first() is not None


class Student(db.Model):
    __tablename__ = 'students'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    enrollment_year = db.Column(db.Integer, nullable=False)
    major = db.Column(db.String(100))
    sgpa = db.Column(db.Float, default=0.0)
    cgpa = db.Column(db.Float, default=0.0)

    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))
    section = db.relationship('Section', backref=db.backref('students', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_student_section', 'section_id'),
    )


class Teacher(db.Model):
    __tablename__ = 'teachers'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    department = db.Column(db.String(100))
    office_hours = db.Column(db.String(200))

    user = db.relationship('User', backref=db.backref('teacher_profile', uselist=False))


# =============================================================================
# ACADEMIC MODELS
# =============================================================================

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    max_students = db.Column(db.Integer, default=50)

    teacher = db.relationship('User', backref=db.backref('taught_courses', lazy='dynamic'))
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic',
                                  cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='course', lazy='dynamic',
                                  cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='course', lazy='dynamic',
                              cascade='all, delete-orphan')
    resources = db.relationship('Resource', backref='course', lazy='dynamic',
                                cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('section_id', 'code', name='uq_course_section_code'),
        db.Index('ix_course_section', 'section_id'),
        db.Index('ix_course_teacher', 'teacher_id'),
    )

    @property
    def school_id(self):
        """Derived school_id via section for isolation checks."""
        return self.section.school_id if self.section else None


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, dropped, completed

    student = db.relationship('User', backref=db.backref('enrollments', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_enrollment_student', 'student_id'),
        db.Index('ix_enrollment_course', 'course_id'),
    )


# =============================================================================
# ASSESSMENT MODELS
# =============================================================================

class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    points = db.Column(db.Integer, nullable=False)

    submissions = db.relationship('Submission', backref='assignment', lazy='dynamic',
                                  cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('ix_assignment_course', 'course_id'),
    )


class Submission(db.Model):
    __tablename__ = 'submissions'

    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    file_url = db.Column(db.String(500))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Float)
    feedback = db.Column(db.Text)

    student = db.relationship('User', backref=db.backref('submissions', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_submission_student', 'student_id'),
    )


class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    time_limit = db.Column(db.Integer)  # minutes
    questions = db.Column(db.Text)  # JSON

    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic',
                               cascade='all, delete-orphan')


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    answers = db.Column(db.Text)  # JSON
    score = db.Column(db.Float)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref=db.backref('quiz_attempts', lazy='dynamic'))


# =============================================================================
# TRACKING MODELS
# =============================================================================

class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late

    course = db.relationship('Course', backref=db.backref('attendance_records', lazy='dynamic'))
    student = db.relationship('User', backref=db.backref('attendance_records', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('course_id', 'student_id', 'date', name='uq_attendance_record'),
        db.Index('ix_attendance_course_date', 'course_id', 'date'),
        db.Index('ix_attendance_student', 'student_id'),
    )


class Grade(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref=db.backref('grades', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('grades', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='uq_grade_student_course'),
        db.Index('ix_grade_student', 'student_id'),
    )


class Streak(db.Model):
    __tablename__ = 'streaks'

    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    current_streak_days = db.Column(db.Integer, default=0)
    last_deadline_met_date = db.Column(db.Date)
    badges_earned = db.Column(db.Text)  # JSON

    student = db.relationship('User', backref=db.backref('streak', uselist=False))


# =============================================================================
# COMMUNICATION MODELS
# =============================================================================

class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)  # NULL = school-wide
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=True) # NULL = school-wide
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    urgent = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), default='general')  # 'general', 'timetable'
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship('Course', backref=db.backref('announcements', lazy='dynamic'))
    section = db.relationship('Section', backref=db.backref('announcements', lazy='dynamic'))
    author = db.relationship('User', backref=db.backref('authored_announcements', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_announcement_school', 'school_id'),
        db.Index('ix_announcement_course', 'course_id'),
        db.Index('ix_announcement_section', 'section_id'),
    )


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id],
                             backref=db.backref('sent_messages', lazy='dynamic'))
    recipient = db.relationship('User', foreign_keys=[recipient_id],
                                backref=db.backref('received_messages', lazy='dynamic'))


class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# USER-CREATED CONTENT
# =============================================================================

class CustomTask(db.Model):
    __tablename__ = 'custom_tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('custom_tasks', lazy='dynamic'))


# =============================================================================
# TIMETABLE
# =============================================================================

class TimetableEntry(db.Model):
    """Per-section timetable entry. Each row = one class slot in the weekly schedule."""
    __tablename__ = 'timetable_entries'

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True) # Link to Course
    day = db.Column(db.Integer, nullable=False)           # 0=Monday, 1=Tuesday, ..., 4=Friday
    start_time = db.Column(db.String(20), nullable=False)  # e.g. '09:00 AM'
    end_time = db.Column(db.String(20), nullable=False)    # e.g. '10:30 AM'
    title = db.Column(db.String(200), nullable=False)      # course/class name
    teacher = db.Column(db.String(100))                     # teacher name
    period = db.Column(db.String(50))                      # e.g. 'Period 1'
    room = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(50), default='var(--primary-color)')
    status = db.Column(db.String(20), default='active')           # 'active', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    section = db.relationship('Section', backref=db.backref('timetable_entries', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('timetable_entries', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_timetable_section', 'section_id'),
    )

    def to_dict(self):
        """Serialize for JSON injection into templates."""
        return {
            'id': self.id,
            'day': self.day,
            'startTime': self.start_time,
            'endTime': self.end_time,
            'title': self.title,
            'subject': self.title,
            'teacher': self.teacher or '',
            'period': self.period or '',
            'room': self.room,
            'color': self.color,
            'status': self.status,
            'course_id': self.course_id,
        }

# =============================================================================
# ADDITIONAL MODELS (Teacher & Social)
# =============================================================================

class TeacherTodo(db.Model):
    __tablename__ = 'teacher_todos'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TeacherRating(db.Model):
    __tablename__ = 'teacher_ratings'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_friend_requests', lazy='dynamic'))
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref=db.backref('received_friend_requests', lazy='dynamic'))

class Friendship(db.Model):
    __tablename__ = 'friendships'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])

# =============================================================================
# FEES MODELS
# =============================================================================

class Fee(db.Model):
    __tablename__ = 'fees'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    tuition_fee = db.Column(db.Float, default=0.0)
    lab_fee = db.Column(db.Float, default=0.0)
    library_fee = db.Column(db.Float, default=0.0)
    exam_fee = db.Column(db.Float, default=0.0)
    other_charges = db.Column(db.Float, default=0.0)
    
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref=db.backref('fee_profile', uselist=False))
    
    @property
    def total_amount(self):
        return (self.tuition_fee or 0) + (self.lab_fee or 0) + (self.library_fee or 0) + (self.exam_fee or 0) + (self.other_charges or 0)
    
    @property
    def amount_paid(self):
        return sum(p.amount for p in self.payments if p.status == 'success')
        
    @property
    def remaining_balance(self):
        return max(0, self.total_amount - self.amount_paid)
        
    @property
    def payment_status(self):
        paid = self.amount_paid
        total = self.total_amount
        if total == 0:
            return 'Paid'
        if paid >= total:
            return 'Paid'
        elif paid > 0:
            return 'Partially Paid'
        else:
            return 'Pending'

class FeePayment(db.Model):
    __tablename__ = 'fee_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    fee_id = db.Column(db.Integer, db.ForeignKey('fees.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # UPI, debit card, credit card, net banking, offline
    status = db.Column(db.String(20), default='pending')  # pending, success, failed
    transaction_id = db.Column(db.String(100), unique=True)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    fee = db.relationship('Fee', backref=db.backref('payments', lazy='dynamic', cascade='all, delete-orphan'))

