from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

main = Blueprint("main", __name__)


@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("projects.view_projects"))
    return redirect(url_for("main.render_login")), 302


@main.route("/register")
def render_register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    return render_template("auth/register.html")


@main.route("/login")
def render_login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    return render_template("auth/login.html")
