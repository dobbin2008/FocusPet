import os
from flask import Flask
from models.database import db
from models import (
    Estudante,
    Pet,
    Tribo,
    BlocoDeNotas,
    SessaoFoco,
    Agenda,
    Estudo,
    ResumoSemanal,
)
from controllers import auth_bp, admin_bp, main_bp


def create_app():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, "focuspet.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 7
    app.secret_key = app.config['SECRET_KEY']

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.drop_all()
        db.create_all()

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

