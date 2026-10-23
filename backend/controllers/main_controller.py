from flask import Blueprint, redirect, url_for

from backend.controllers.auth_controller import developer_required, login_required, pagina_estatica

main_bp = Blueprint("main", __name__)


class MainController:
    @login_required
    def index(self):
        return pagina_estatica("index.html")

    @login_required
    def dashboard(self):
        return redirect(url_for("main.index"))

    @developer_required
    def developer(self):
        return pagina_estatica("index.html")


main_controller = MainController()
main_bp.add_url_rule("/", view_func=main_controller.index, methods=["GET"])
main_bp.add_url_rule("/dashboard", view_func=main_controller.dashboard, methods=["GET"])
main_bp.add_url_rule("/desenvolvedor", view_func=main_controller.developer, methods=["GET"])