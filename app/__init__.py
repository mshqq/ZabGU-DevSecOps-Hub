import os

from flask import Flask

from app.extensions import db, login_manager, migrate


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    secret = os.getenv("FLASK_SECRET")
    if not secret:
        raise RuntimeError("FLASK_SECRET не задан - см. .env.example")

    app.config.update(
        SECRET_KEY=secret,
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL",
            "sqlite:///zabgu-devsecops.db",
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    app.json.sort_keys = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import models  # noqa: F401

    return app
