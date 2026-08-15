from collections import defaultdict

from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from app.models.finding import Finding
from app.models.project import Project
from app.models.scan import Scan

scan_bp = Blueprint("scan", __name__)


@scan_bp.route("/api/scans/<int:scan_id>", methods=["GET"])
@login_required
def scan_status(scan_id):
    scan = (
        Scan.query.options(joinedload(Scan.project)).filter(Scan.id == scan_id).first()
    )
    if not scan or scan.project.owner_id != current_user.id:
        return jsonify({"error": "Данного скана не существует"}), 404
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


def group_sort_severity(findings):
    grouped = defaultdict(list)
    for f in findings:
        grouped[f["severity"]].append(f)
    for finding_list in grouped.values():
        finding_list.sort(key=lambda x: x["file_path"])
    summary = {
        severity: len(finding_list) for severity, finding_list in grouped.items()
    }
    return dict(grouped), summary


def findings(scan_id):
    scan = (
        Scan.query.options(joinedload(Scan.project)).filter(Scan.id == scan_id).first()
    )
    if not scan or scan.project.owner_id != current_user.id:
        return None, None, (jsonify({"error": "Данного скана не существует"}), 404)
    if scan.status == "failed":
        return None, None, (jsonify({"error": scan.error_message}), 409)
    if scan.status != "done":
        return None, None, (jsonify({"status": scan.status}), 409)
    finding = Finding.query.filter(
        Scan.id == scan_id, Project.owner_id == current_user.id
    ).all()
    if scan.status == "done":
        findings = [
            {
                "id": f.id,
                "rule_id": f.rule_id,
                "severity": f.severity,
                "confidence": f.confidence,
                "source": f.source,
                "file_path": f.file_path,
                "line_no": f.line_no,
                "commit_sha": f.commit_sha,
                "masked_value": f.masked_value,
                "context": f.context,
                "status": f.status,
            }
            for f in finding
        ]
    grouped, summary = group_sort_severity(findings)
    return scan, (summary, grouped), None


@scan_bp.route("/api/scans/<int:scan_id>/report", methods=["GET"])
@login_required
def report_json(scan_id):
    scan, data, err = findings(scan_id)
    if err:
        return err
    summary, grouped = data
    return jsonify(
        {
            "scan_id": scan.id,
            "project_id": scan.project.id,
            "commit_sha": scan.commit_sha,
            "truncated": scan.truncated,
            "finished_at": scan.finished_at,
            "summary": summary,
            "findings": grouped,
        }
    )


@scan_bp.route("/api/scans/<int:scan_id>/report.md", methods=["GET"])
@login_required
def report_md(scan_id):
    scan, data, err = findings(scan_id)
    if err:
        return err
    summary, grouped = data
    context = {
        "summary": summary,
        "grouped": grouped,
        "project_title": scan.project.title,
        "repo_url": scan.project.repo_url,
        "scan_id": scan.id,
        "commit_sha": scan.commit_sha,
        "finished_at": scan.finished_at,
        "truncated": scan.truncated,
    }
    return render_template("/reports/scan_report.md", **context)
