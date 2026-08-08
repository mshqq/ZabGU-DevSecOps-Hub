from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
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
