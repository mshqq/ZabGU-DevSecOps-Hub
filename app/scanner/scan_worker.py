from concurrent.futures import Future, ThreadPoolExecutor

from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.finding import Finding
from app.models.scan import Scan
from app.scanner.base import ScanContext
from app.scanner.clone import cleanup, clone_repo
from app.scanner.files import list_files
from app.scanner.runner import ScanResult, run_rules
from app.utils import utcnow

executor = ThreadPoolExecutor(max_workers=4)


def run_scan(app, scan_id: int) -> Future:
    return executor.submit(worker_function, app, scan_id)


def worker_function(app, scan_id) -> ScanResult | None:
    with app.app_context():
        scan: Scan | None = (
            Scan.query.options(joinedload(Scan.project))
            .filter(Scan.id == scan_id)
            .first()
        )
        repo_url: str = scan.project.repo_url
        repo_path: str | None = None
        print(f"Начинаю обработку {repo_url}")
        scan.status = "running"
        scan.started_at = utcnow()
        db.session.commit()

        try:
            repo_path, resolved_sha = clone_repo(repo_url)

            ctx = ScanContext(repo_path, resolved_sha, list_files(repo_path))
            result: ScanResult = run_rules(ctx)

            scan.status = "done"
            scan.truncated = result.truncated
            scan.error_message = "; ".join(result.errors)

            for f in result.findings:
                # pyrefly: ignore [unexpected-keyword]
                finding = Finding(
                    # pyrefly: ignore [unexpected-keyword]
                    scan_id=scan_id,
                    # pyrefly: ignore [unexpected-keyword]
                    rule_id=f["rule_id"],
                    # pyrefly: ignore [unexpected-keyword]
                    severity=f["severity"],
                    # pyrefly: ignore [unexpected-keyword]
                    confidence=f["confidence"],
                    # pyrefly: ignore [unexpected-keyword]
                    source=f["source"],
                    # pyrefly: ignore [unexpected-keyword]
                    file_path=f["file_path"],
                    # pyrefly: ignore [unexpected-keyword]
                    line_no=f["line_no"],
                    # pyrefly: ignore [unexpected-keyword]
                    commit_sha=f["commit_sha"],
                    # pyrefly: ignore [unexpected-keyword]
                    masked_value=f["masked_value"],
                    # pyrefly: ignore [unexpected-keyword]
                    context=f["context"],
                )
                db.session.add(finding)

            scan.finished_at = utcnow()
            db.session.commit()

        except Exception as e:
            scan.status = "failed"
            scan.error_message = str(e)
            db.session.commit()
            return
        finally:
            if repo_path:
                cleanup(repo_path)

    print("Поток завершил работу")
