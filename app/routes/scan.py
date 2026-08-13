from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from app.models import Project
from app.models.scan import Scan

scan_bp = Blueprint("scan", __name__)


@scan_bp.route("/api/scans/<int:scan_id>", methods=["GET"])
@login_required
def scan_status(scan_id):
    scan = Scan.query.filter(
        Scan.id == scan_id, Project.owner_id == current_user.id
    ).first()
    if not scan:
        return jsonify({"error": "Нет сканов"}), 404
    return jsonify(
        {
            "status": scan.status,
            "started_at": scan.started_at,
            "finished_at": scan.finished_at,
            "commit_sha": scan.commit_sha,
            "truncated": scan.truncated,
            "error_message": scan.error_message,
            "created_at": scan.created_at,
        }
    ), 200
