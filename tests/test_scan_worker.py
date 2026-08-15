from app.models.finding import Finding
from app.models.scan import Scan
from app.scanner.scan_worker import run_scan


def test_concurrent(app, user, project, scan):
    future = run_scan(app, scan.id)
    future.result(timeout=60)

    with app.app_context():
        completed_scan = Scan.query.filter(Scan.id == scan.id).first()
        findings = Finding.query.all()

    assert completed_scan.status == "done"
    assert findings
    assert all(f.rule_id == "ENV_FILE_COMMITED" for f in findings)
