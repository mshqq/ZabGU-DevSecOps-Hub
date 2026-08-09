from flask import Blueprint, abort, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.project import Project

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/api/projects", methods=["POST", "GET"])
@login_required
def projects():
    if request.method == "GET":
        projects = Project.query.filter_by(owner_id=current_user.id).all()
        return jsonify(
            {
                p.id: {"title": p.title, "repo_url": p.repo_url, "provider": p.provider}
                for p in projects
            }
        ), 200

    data = request.get_json()
    if not data:
        return jsonify({"error": "запрос не содержит json"}), 400
    title = data.get("title")
    repo_url = data.get("repo_url")
    provider = data.get("provider")
    if not title or not repo_url:
        return jsonify({"error": "Строки не могут быть пустыми"}), 400
    if provider not in ["github", "gitlab"]:
        return jsonify({"error": "Неизвестный провайдер"}), 400
    owner_id = current_user.id
    project = Project(
        title=title, repo_url=repo_url, provider=provider, owner_id=owner_id
    )
    project.create_ownership_token()
    try:
        db.session.add(project)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Данный проект уже добавлен"}), 400
    return jsonify(
        {
            "message": "Проект успешно добавлен",
            "id": project.id,
            "ownership_token": project.ownership_token,
        }
    ), 201


@projects_bp.route("/api/projects/<int:project_id>", methods=["GET"])
@login_required
def project_info(project_id):
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first()

    if project is None:
        return jsonify({"error": "Проект не найден"}), 404

    return jsonify(
        {
            "id": project.id,
            "title": project.title,
            "repo_url": project.repo_url,
            "provider": project.provider,
        }
    ), 200


@projects_bp.route("/api/projects/<int:project_id>", methods=["DELETE"])
@login_required
def delete_project(project_id):
    project = Project.query.get(project_id)

    if project is None:
        return jsonify({"error": "Проект не найден"}), 404

    if project.owner_id != current_user.id:
        abort(403)

    db.session.delete(project)
    db.session.commit()

    return jsonify({"message": "Проект удален"}), 200
