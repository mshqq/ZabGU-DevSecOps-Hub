import secrets

from app.extensions import db
from app.utils import utcnow


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    title = db.Column(db.String(200), nullable=False)
    repo_url = db.Column(db.String(500), nullable=False)
    provider = db.Column(db.String(16), nullable=False)  # github
    ownership_token = db.Column(db.String(64), nullable=False)
    ownership_verified_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    owner = db.relationship("User", back_populates="projects")
    scans = db.relationship(
        "Scan", back_populates="project", cascade="all, delete-orphan"
    )

    __table_args__ = (db.UniqueConstraint("owner_id", "repo_url"),)

    def create_ownership_token(self):
        self.ownership_token = secrets.token_urlsafe(16)
