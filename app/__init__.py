import os
from datetime import timezone, timedelta
from flask import Flask
from config import Config
from .extensions import db, login_manager
from .routes.auth import auth_bp
from .routes.main import main_bp
from .routes.goals import goals_bp
from .routes.analysis import analysis_bp
from .routes.reflection import reflection_bp
from .routes.profile import profile_bp

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(goals_bp, url_prefix="/goals")
    app.register_blueprint(analysis_bp, url_prefix="/analysis")
    app.register_blueprint(reflection_bp, url_prefix="/reflections")
    app.register_blueprint(profile_bp, url_prefix="/profile")

    _JST = timezone(timedelta(hours=9))

    @app.template_filter("jst")
    def jst_filter(dt, fmt="%Y-%m-%d %H:%M"):
        if dt is None:
            return ""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(_JST).strftime(fmt)

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database initialized.")

    return app
