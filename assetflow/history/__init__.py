from flask import Blueprint

bp = Blueprint("history", __name__, template_folder="../templates/history")

from . import routes  # noqa: E402,F401
