from flask import Blueprint, redirect, render_template, session, url_for

main_bp = Blueprint("main", __name__, url_prefix="")


class MainController:
    def index(self):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("index.html")

    def dashboard(self):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("dashboard.html")


main_controller = MainController()
main_bp.add_url_rule("/", view_func=main_controller.index)
main_bp.add_url_rule("/dashboard", view_func=main_controller.dashboard)
