from app.extensions import db


class Finding(db.Model):
    __tablename__ = "findings"

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(
        db.Integer, db.ForeignKey("scans.id"), nullable=False, index=True
    )
    rule_id = db.Column(db.String(64), nullable=False, index=True)
    severity = db.Column(db.String(2), nullable=False, index=True)
    confidence = db.Column(db.String(8), nullable=False)
    source = db.Column(db.String(8), nullable=False)
    file_path = db.Column(db.String(1000), nullable=False)
    line_no = db.Column(db.Integer)
    commit_sha = db.Column(db.String(40))
    masked_value = db.Column(db.String(500))
    context = db.Column(db.JSON, default=dict)
    status = db.Column(db.String(16), default="new", nullable=False)

    scan = db.relationship("Scan", back_populates="findings")
