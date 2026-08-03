from flask import Blueprint, redirect, render_template, session, url_for

main_bp = Blueprint("main", __name__, url_prefix="")


@main_bp.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("index.html")


@main_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html")
