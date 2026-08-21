import os
from flask import Flask
from sqlalchemy import inspect, text
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
    ListaBloqueada,
)
from controllers import (
    agenda_bp,
    auth_bp,
    admin_bp,
    blacklist_bp,
    foco_bp,
    main_bp,
    notas_bp,
)


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
    app.register_blueprint(agenda_bp)
    app.register_blueprint(notas_bp)
    app.register_blueprint(foco_bp)
    app.register_blueprint(blacklist_bp)

    with app.app_context():
        db.create_all()
        if "estudos" in inspect(db.engine).get_table_names():
            colunas_estudos = {
                coluna["name"] for coluna in inspect(db.engine).get_columns("estudos")
            }
            if "titulo" not in colunas_estudos:
                db.session.execute(text(
                    "ALTER TABLE estudos ADD COLUMN titulo VARCHAR(200) NOT NULL DEFAULT 'Estudo'"
                ))
                db.session.commit()

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

