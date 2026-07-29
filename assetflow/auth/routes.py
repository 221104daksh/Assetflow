from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from . import bp
from ..extensions import db
from ..models import User
from ..forms import LoginForm
from ..utils import log_action
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()

    print("=" * 60)
    print("REQUEST METHOD:", request.method)
    print("FORM VALID:", form.validate_on_submit())
    print("FORM ERRORS:", form.errors)
    print("=" * 60)

    if form.validate_on_submit():

        print("=" * 60)
        print("LOGIN ATTEMPT")
        print("Username:", form.username.data)

        user = User.query.filter_by(
            username=form.username.data.strip()
        ).first()

        print("User:", user)

        if user:
            print("Password Entered:", form.password.data)
            print("Password Match:", user.check_password(form.password.data))
            print("Stored Hash:", user.password_hash)
        else:
            print("User not found")

        print("=" * 60)

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)

            user.last_login = datetime.utcnow()
            db.session.commit()

            log_action("User Login")

            print("LOGIN SUCCESSFUL")

            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))

        print("LOGIN FAILED")
        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html", form=form)