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

    if form.validate_on_submit():

        print("\n" + "=" * 60)
        print("LOGIN ATTEMPT")
        print("=" * 60)
        print("Username Entered :", form.username.data)

        user = User.query.filter_by(
            username=form.username.data.strip()
        ).first()

        print("User Found       :", user)

        if user:
            print("User ID          :", user.id)
            print("Username         :", user.username)
            print("Email            :", user.email)
            print("Role             :", user.role)
            print("Password Hash    :", user.password_hash)
            print(
                "Password Match   :",
                user.check_password(form.password.data)
            )
        else:
            print("❌ No user found with this username.")

        print("=" * 60)

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)

            user.last_login = datetime.utcnow()
            db.session.commit()

            log_action("User Login")

            print("✅ Login Successful")
            print("=" * 60)

            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))

        print("❌ Login Failed")
        print("=" * 60)

        flash("Invalid username or password.", "danger")

    else:
        if request.method == "POST":
            print("\n" + "=" * 60)
            print("FORM VALIDATION FAILED")
            print(form.errors)
            print("=" * 60)

    return render_template("auth/login.html", form=form)