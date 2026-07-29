from flask import Blueprint

bp = Blueprint("qr", __name__, template_folder="../templates/qr")
public_bp = Blueprint("public", __name__, template_folder="../templates/qr")

from . import routes  # noqa: E402,F401
