import os
from flask import Flask
from database import fechar_banco, inicializar_banco
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
    app.config['DATABASE'] = db_path
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 7
    app.secret_key = app.config['SECRET_KEY']

    inicializar_banco(db_path)
    app.teardown_appcontext(fechar_banco)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(agenda_bp)
    app.register_blueprint(notas_bp)
    app.register_blueprint(foco_bp)
    app.register_blueprint(blacklist_bp)

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

