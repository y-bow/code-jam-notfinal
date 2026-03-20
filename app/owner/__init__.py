from flask import Blueprint

owner_bp = Blueprint('owner', __name__, template_folder='../../templates/owner')

from . import routes
