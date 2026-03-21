# Hive — Open Source University LMS
### The Smarter Way to Manage Higher Education

A university Learning Management System (LMS) prototype built for FOSS Hack 2026. This platform features multi-tenant architecture with role-based access control for Deans, Professors, and Students.

- **Multi-tenancy**: Data isolated per school.
- **Role-based Access**: Custom dashboards and permissions for students, professors, and administrators.
- **Classroom Management**: Course enrollments, assignments, and resource sharing.
- **Timetable**: Section-specific weekly schedules.
- **Announcements & Messaging**: Real-time communication within schools and courses.

## Folder Structure
```text
.
├── app/                # Core application package
│   ├── routes/         # Flask Blueprints (auth, dashboard, classroom)
│   ├── models.py       # SQLAlchemy database models
│   ├── middleware.py   # Tenant isolation & RBAC logic
│   └── __init__.py     # Application factory
├── static/             # Frontend assets (CSS, JS)
├── templates/          # HTML templates
├── run.py              # Application entry point
├── .env.example        # Environment variable template
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## Installation Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/vaibhav/Code-JAM.git
   cd Code-JAM
   ```
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/scripts/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. **Initialize the database**:
   ```bash
   python init_db.py
   ```
6. **Run the application**:
   ```bash
   python run.py
   ```

## Usage Instructions
- Access the application at `http://127.0.0.1:5000`.
- Log in with credentials provided by your institution.

## Contribution Guidelines
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
