import os

from flask import Blueprint, redirect, send_from_directory, session, url_for

main_bp = Blueprint("main", __name__, url_prefix="")


def pagina_estatica(nome):
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"), nome)


class MainController:
    def index(self):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return pagina_estatica("index.html")

    def dashboard(self):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return pagina_estatica("dashboard.html")


main_controller = MainController()
main_bp.add_url_rule("/", view_func=main_controller.index)
main_bp.add_url_rule("/dashboard", view_func=main_controller.dashboard)
