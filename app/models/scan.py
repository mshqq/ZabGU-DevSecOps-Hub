from app.extensions import db
from app.utils import utcnow


class Scan(db.Model):
    __tablename__ = "scans"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True
    )
    status = db.Column(db.String(16), default="queued", nullable=False, index=True)
    # queued | running | done | failed
    started_at = db.Column(db.DateTime(timezone=True))
    finished_at = db.Column(db.DateTime(timezone=True))
    commit_sha = db.Column(db.String(40))
    truncated = db.Column(db.Boolean, default=False, nullable=False)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    project = db.relationship("Project", back_populates="scans")
    findings = db.relationship(
        "Finding", back_populates="scan", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Scan {self.id} {self.status}>"
