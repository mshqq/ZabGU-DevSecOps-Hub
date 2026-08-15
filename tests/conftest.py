import os

import pytest

from app import create_app
from app.extensions import db
from app.models.project import Project
from app.models.scan import Scan
from app.models.user import User
from app.utils import utcnow

os.environ.setdefault("FLASK_SECRET", "test-secret")


@pytest.fixture
def app():
    # pyrefly: ignore [unexpected-keyword]
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret-key",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def user(app):
    u = User(email="mshqq@email.test")
    u.set_password("TEST_PASSWORD")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def project(app, user):
    p = Project(
        owner_id=user.id,
        title="Тестовый проект",
        repo_url="https://github.com/mshqq/ZabGU-DevSecOps-Hub",
        provider="github",
    )
    p.create_ownership_token()
    db.session.add(p)
    db.session.commit()
    return p


@pytest.fixture
def scan(app, user, project):
    s = Scan(
        project_id=project.id,
        status="done",
        started_at=utcnow(),
        finished_at=utcnow(),
        commit_sha="0" * 40,
        truncated=False,
    )
    db.session.add(s)
    db.session.commit()
    return s
