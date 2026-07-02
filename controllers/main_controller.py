from flask import Blueprint, redirect, render_template, session, url_for

main_bp = Blueprint("main", __name__, url_prefix="")


@main_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")


@main_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
