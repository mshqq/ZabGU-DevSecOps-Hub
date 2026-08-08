from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return jsonify({"message": "Пользователь уже авторизован"}), 409
    data = request.get_json()
    if not data:
        return jsonify({"error": "запрос не содержит json"}), 400
    email = data.get("email")
    if "@" not in email:
        return jsonify({"error": "неверный формат email"}), 400
    password = data.get("password")
    if len(password) < 8:
        return jsonify({"error": "Пароль должен быть не менее 8 символов"}), 400
    if not email or not password:
        return jsonify({"error": "неверный логин или пароль"}), 400
    # pyrefly: ignore [unexpected-keyword]
    user = User(email=email)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Пользователь с таким email уже существует"}), 400

    return jsonify({"message": "Пользователь создан"}), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return jsonify({"message": "Пользователь уже авторизован"}), 409
    data = request.get_json()
    if not data:
        return jsonify({"error": "запрос не содержит json"}), 400
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "не указан логин или пароль"}), 400
    user = User.query.filter_by(email=email).first()
    if not user.check_password(password) or not user:
        return jsonify({"error": "неверный логин или пароль"}), 401
    login_user(user)
    return jsonify({"message": "Успешный вход"}), 200


@auth_bp.route("/api/auth/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Успешный выход"}), 200


@auth_bp.route("/api/whoami", methods=["GET"])
@login_required
def whoami():
    return jsonify({"id": current_user.id, "email": current_user.email})
