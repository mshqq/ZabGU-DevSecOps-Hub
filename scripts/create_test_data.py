from dotenv import load_dotenv

from app import create_app
from app.extensions import db
from app.models.finding import Finding
from app.models.project import Project
from app.models.scan import Scan
from app.models.user import User
from app.utils import utcnow

TEST_EMAIL = "mshqq@email.test"
TEST_PASSWORD = "TestPassword123!"
TEST_REPO_URL = "https://github.com/mshqq/mshqq"


def create_test_user() -> User:
    user = User.query.filter_by(email=TEST_EMAIL).first()
    if user is not None:
        print(f"Пользователь уже существует: {user.email}")
        return user

    user = User(email=TEST_EMAIL)
    user.set_password(TEST_PASSWORD)
    db.session.add(user)
    db.session.flush()
    print(f"Создан пользователь: {user.email} (пароль: {TEST_PASSWORD})")
    return user


def create_test_project(user: User) -> Project:
    project = Project.query.filter_by(owner_id=user.id, repo_url=TEST_REPO_URL).first()
    if project is not None:
        print(f"Проект уже существует: {project.title} (id={project.id})")
        return project

    project = Project(
        owner_id=user.id,
        title="Тестовый проект",
        repo_url=TEST_REPO_URL,
        provider="github",
    )
    project.create_ownership_token()
    project.ownership_verified_at = utcnow()
    db.session.add(project)
    db.session.flush()
    print(f"Создан проект: {project.title} (id={project.id})")
    return project


def create_test_scan(project: Project) -> Scan:
    scan = Scan(
        project_id=project.id,
        status="done",
        started_at=utcnow(),
        finished_at=utcnow(),
        commit_sha="0" * 40,
        truncated=False,
    )
    db.session.add(scan)
    db.session.flush()
    print(f"Создан скан: id={scan.id}, status={scan.status}")
    return scan


def create_test_finding(scan: Scan) -> Finding:
    finding = Finding(
        scan_id=scan.id,
        rule_id="ENV_FILE_COMMITED",
        severity="P0",
        confidence="high",
        source="regex",
        file_path=".env",
        line_no=3,
        commit_sha=scan.commit_sha,
        masked_value="test****test",
        context={"key": "API_KEY"},
    )
    db.session.add(finding)
    db.session.flush()
    print(f"Создан finding: id={finding.id}, rule_id={finding.rule_id}")
    return finding


def seed() -> None:
    user = create_test_user()
    project = create_test_project(user)
    scan = create_test_scan(project)
    create_test_finding(scan)
    db.session.commit()


if __name__ == "__main__":
    load_dotenv()
    app = create_app()
    with app.app_context():
        seed()
