import os
from flask import Flask, redirect, url_for, session
from dotenv import load_dotenv
from .models import db, bcrypt

load_dotenv()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    # Configuration
    # Safe absolute pathing for SQLite on Windows (uses 4 slashes)
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, 'app.db').replace('\\', '/')
    if not db_path.startswith('/'):
        db_path = '/' + db_path
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite://{db_path}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    @app.template_filter('fix_time')
    def fix_time_filter(s):
        return s.replace(" ", "") if s else s

    @app.context_processor
    def inject_globals():
        from flask import session
        from .models import School
        school_id = session.get('school_id')
        school = School.query.get(school_id) if school_id else None
        
        # Determine school name: if global admin (no school_id), then 'Hive' or empty
        # If school exists, use its name. Fallback to session or 'Platform'
        if not school_id:
            # Platform Owner (Global Admin)
            school_name = None
        else:
            school_name = school.name if school else session.get('school_name', 'Your University')
            
        return dict(
            school=school,
            school_name=school_name,
            app_name='Hive',
            platform_version='1.0.4'
        )

    # Session Security
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=1800, # 30 minutes
    )

    @app.after_request
    def add_header(response):
        """
        Prevent browser caching of sensitive pages to avoid 'account swapping'
        when multiple users use the same machine/browser.
        """
        if 'user_id' in session:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.classroom import classroom_bp
    from .routes.messages import messages_bp
    from .routes.fees import fees_bp
    from .routes.internships import internships_bp
    from .routes.lost_found import lost_found_bp
    from .routes.clubs import clubs_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(classroom_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(fees_bp)
    app.register_blueprint(internships_bp)
    app.register_blueprint(lost_found_bp)
    app.register_blueprint(clubs_bp)

    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('role')
            if role in ('student', 'class_rep'):
                return redirect(url_for('dashboard.student_dashboard'))
            elif role in ('professor', 'assistant_professor'):
                return redirect(url_for('dashboard.teacher_dashboard'))
            elif role == 'dean':
                return redirect(url_for('dashboard.school_analytics'))
            elif role == 'admin':
                return redirect(url_for('dashboard.admin_dashboard'))
        return redirect(url_for('auth.login'))

    return app
