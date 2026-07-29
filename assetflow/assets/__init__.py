from flask import Blueprint

bp = Blueprint("assets", __name__, template_folder="../templates/assets")

from . import routes  # noqa: E402,F401
