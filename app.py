import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from backend.database import db, inicializar_banco
from backend.controllers import (
    agenda_bp,
    auth_bp,
    blacklist_bp,
    dashboard_bp,
    developer_bp,
    foco_bp,
    historico_foco_bp,
    main_bp,
    materias_bp,
    metas_bp,
    notas_bp,
    pet_bp,
    perfil_bp,
    summary_bp,
)


def create_app(test_config=None):
    load_dotenv()
    basedir = Path(__file__).resolve().parent
    app = Flask(__name__, static_folder="frontend/static", static_url_path="/static")
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY") or secrets.token_hex(32),
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL", f"sqlite:///{basedir / 'focuspet.db'}"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        PROFILE_UPLOAD_FOLDER=str(Path(app.instance_path) / "profile_photos"),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
        TURNSTILE_SITE_KEY=os.getenv("TURNSTILE_SITE_KEY", ""),
        TURNSTILE_SECRET_KEY=os.getenv("TURNSTILE_SECRET_KEY", ""),
        DEVELOPER_EMAIL=os.getenv("DEVELOPER_EMAIL", "").strip().lower(),
        SESSION_PERMANENT=True,
        PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(materias_bp)
    app.register_blueprint(metas_bp)
    app.register_blueprint(agenda_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(developer_bp)
    app.register_blueprint(notas_bp)
    app.register_blueprint(pet_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(summary_bp)
    app.register_blueprint(foco_bp)
    app.register_blueprint(historico_foco_bp)
    app.register_blueprint(blacklist_bp)

    with app.app_context():
        inicializar_banco()
    return app


if __name__ == '__main__':
    create_app().run(debug=os.getenv("FLASK_DEBUG", "0") == "1", host="127.0.0.1", port=5000)
