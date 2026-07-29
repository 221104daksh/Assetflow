import os
from flask import Flask, render_template
from config import Config, basedir
from assetflow.extensions import (
    db,
    migrate,
    login_manager,
    bcrypt,
    csrf,
    cache,
)


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder="assetflow/templates",
        static_folder="assetflow/static",
    )

    app.config.from_object(config_class)

    # --------------------------------------------------
    # Create required folders
    # --------------------------------------------------
    instance_dir = os.path.join(basedir, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # --------------------------------------------------
    # Debug Info
    # --------------------------------------------------
    print("=" * 60)
    print("Working Directory :", os.getcwd())
    print("Root Path         :", app.root_path)
    print("Instance Folder   :", instance_dir)
    print("Database URI      :", app.config["SQLALCHEMY_DATABASE_URI"])
    print("=" * 60)

    # --------------------------------------------------
    # Initialize Extensions
    # --------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)

    # --------------------------------------------------
    # Import Models
    # --------------------------------------------------
    from assetflow.models import (
        User,
        Employee,
        Asset,
        AuditLog,
        Setting,
    )

    # --------------------------------------------------
    # Create Database Tables
    # --------------------------------------------------
    with app.app_context():

        print("=" * 60)
        print("Creating database tables...")
        print("=" * 60)

        db.create_all()

        # ---------------- Default Settings ----------------
        defaults = {
            "org_name": "AssetFlow",
            "org_logo": "",
            "theme_color": "#4361ee",
            "footer_text": "AssetFlow — IT Asset Management",
        }

        for key, value in defaults.items():
            setting = Setting.query.filter_by(key=key).first()

            if setting is None:
                db.session.add(
                    Setting(
                        key=key,
                        value=value,
                    )
                )

        # ---------------- Create / Reset Admin ----------------
        admin = User.query.filter_by(username="admin").first()

        if admin is None:

            print("Creating admin user...")

            admin = User(
                name="Administrator",
                username="admin",
                email="admin@example.com",
                role="admin",
            )

            admin.set_password("admin123")
            db.session.add(admin)

        else:

            print("Admin already exists.")
            print("Resetting admin password...")

            admin.name = "Administrator"
            admin.email = "admin@example.com"
            admin.role = "admin"

            admin.set_password("admin123")

        db.session.commit()

        print("=" * 60)
        print("Database initialized successfully.")
        print(f"Total Users: {User.query.count()}")

        for user in User.query.all():
            print(
                f"ID={user.id}, "
                f"Username={user.username}, "
                f"Email={user.email}, "
                f"Role={user.role}"
            )

        print("=" * 60)

    # --------------------------------------------------
    # Login Manager
    # --------------------------------------------------
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    # --------------------------------------------------
    # Register Blueprints
    # --------------------------------------------------
    from assetflow.auth import bp as auth_bp
    from assetflow.dashboard import bp as dashboard_bp
    from assetflow.employees import bp as employees_bp
    from assetflow.assets import bp as assets_bp
    from assetflow.history import bp as history_bp
    from assetflow.qr import bp as qr_bp, public_bp
    from assetflow.settings import bp as settings_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(employees_bp, url_prefix="/employees")
    app.register_blueprint(assets_bp, url_prefix="/assets")
    app.register_blueprint(history_bp, url_prefix="/history")
    app.register_blueprint(qr_bp, url_prefix="/qr")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(public_bp)

    # --------------------------------------------------
    # Root Route
    # --------------------------------------------------
    @app.route("/")
    def root():
        from flask import redirect, url_for
        from flask_login import current_user

        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))

        return redirect(url_for("auth.login"))

    # --------------------------------------------------
    # Error Handlers
    # --------------------------------------------------
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # --------------------------------------------------
    # Global Template Variables
    # --------------------------------------------------
    @app.context_processor
    def inject_globals():
        try:
            return {
                "org_name": Setting.get("org_name", "AssetFlow"),
                "org_logo": Setting.get("org_logo", ""),
                "theme_color": Setting.get("theme_color", "#4361ee"),
                "footer_text": Setting.get(
                    "footer_text",
                    "AssetFlow — IT Asset Management",
                ),
            }
        except Exception:
            db.session.rollback()
            return {
                "org_name": "AssetFlow",
                "org_logo": "",
                "theme_color": "#4361ee",
                "footer_text": "AssetFlow — IT Asset Management",
            }

    return app


# --------------------------------------------------
# Create Application
# --------------------------------------------------
app = create_app()


# --------------------------------------------------
# Run Development Server
# --------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )