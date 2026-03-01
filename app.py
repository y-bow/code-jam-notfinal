from flask import Flask, render_template, redirect, url_for
from models import db, bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)

from auth import auth_bp
app.register_blueprint(auth_bp)

from dashboard import dashboard_bp
app.register_blueprint(dashboard_bp)

from classroom import classroom_bp
app.register_blueprint(classroom_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
