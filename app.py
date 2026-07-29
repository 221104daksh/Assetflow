import os
from flask import Flask, render_template
from config import Config, basedir
from assetflow.extensions import db, migrate, login_manager, bcrypt, csrf, cache

def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder="assetflow/templates",
        static_folder="assetflow/static",
    )

    app.config.from_object(config_class)

    # Create the SAME instance folder used by config.py
    instance_dir = os.path.join(basedir, "instance")
    os.makedirs(instance_dir, exist_ok=True)

    # Upload folder
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Debug (remove later)
    print("=" * 60)
    print("Working Directory :", os.getcwd())
    print("Root Path         :", app.root_path)
    print("Instance Folder   :", instance_dir)
    print("Database URI      :", app.config["SQLALCHEMY_DATABASE_URI"])
    print("=" * 60)

    # -------- Extensions --------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)

    from assetflow.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -------- Blueprints --------
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

    @app.route("/")
    def root():
        from flask import redirect, url_for
        from flask_login import current_user

        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    @app.context_processor
    def inject_globals():
        from assetflow.models import Setting

        return {
            "org_name": Setting.get("org_name", "AssetFlow"),
            "org_logo": Setting.get("org_logo", ""),
            "theme_color": Setting.get("theme_color", "#4361ee"),
            "footer_text": Setting.get(
                "footer_text",
                "AssetFlow — IT Asset Management",
            ),
        }

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
