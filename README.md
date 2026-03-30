# 🛡️ Hive LMS Prototype - Code-JAM

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask: 3.0.2](https://img.shields.io/badge/Flask-3.0.2-green.svg)](https://flask.palletsprojects.com/)

A modern, multi-tenant university Learning Management System (LMS) prototype designed for **FOSS Hack 2026**. This platform provides granular data isolation per school, role-based access control, and a rich, interactive dashboard for various stakeholders.

---

## ✨ Key Features

| Feature                | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| **Multi-tenancy**      | Full data isolation between different schools and departments.        |
| **RBAC**               | Distinct dashboards for **Admins**, **Deans**, **Professors**, and **Students**. |
| **Course Management**  | Integrated enrollment, assignment tracking, and resource management.        |
| **Timetable System**   | Dynamic, section-specific schedules with color-coded course categories.    |
| **Analytics**          | Real-time insights into student performance and teacher ratings.      |
| **Early Warning**      | Automated flags for at-risk students based on attendance and performance. |

## 📁 Project Structure

```text
.
├── app/                # Core Flask application package
│   ├── routes/         # Feature-specific blueprints (auth, dashboard, classroom, etc.)
│   ├── models.py       # SQLAlchemy database models & schemas
│   ├── permissions.py  # Role-based access control decorators
│   └── __init__.py     # Application factory and configuration
├── static/             # Static assets (CSS frameworks, images, JS modules)
├── templates/          # Jinja2 HTML templates
├── instance/           # Default location for the SQLite database
├── run.py              # Main entry point with auto-seeding logic
├── init_db.py          # Standalone database initialization and seeding script
├── .env.example        # Template for environment variables
└── requirements.txt    # Python dependencies
```

## 🛠️ Installation & Setup

Follow these steps to get Hive LMS running locally:

### 1. Prerequisites
- **Python 3.10+** (tested on 3.14 for development)
- **pip** (Python package manager)

### 2. Environment Setup
```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
```bash
# Create your local .env file
cp .env.example .env
# Open .env and set your SECRET_KEY
```

### 4. Database Setup
```bash
# Initialize the database with fresh seed data
python init_db.py
```

### 5. Running the App
```bash
# Start the development server
python run.py

# Optional: Force a fresh reseed on startup
# python run.py --reseed
```

---

## 🧪 Testing Credentials

To test the multi-tenant and role-based features, you can use the following default accounts. All accounts use the default password: **`hive@1234`**.

| Role           | Email                                    | Access Level                    |
|----------------|------------------------------------------|---------------------------------|
| **Global Admin**| `admin@saiuniversity.edu.in`             | Full system management        |
| **Dean**        | `dean@scds.saiuniversity.edu.in`         | School-wide analytics view      |
| **Professor**   | `professor@scds.saiuniversity.edu.in`    | Course & student management      |
| **Student**     | `sripadagayathri.l-29@scds.saiuniversity.edu.in` | Personalized student dashboard |

> [!NOTE]
> **CAPTCHA Bypass**: For development and testing environments, the backend CAPTCHA check is currently disabled. You can enter any character string in the CAPTCHA field on the login page to proceed.

## 🤝 Contribution

Contributions are welcome! Please check our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

