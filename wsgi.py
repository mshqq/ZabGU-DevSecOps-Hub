from os import getenv

from dotenv import load_dotenv

from app import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    debug = getenv("FLASK_DEBUG", "0") == "1"
    host = getenv("FLASK_HOST", "127.0.0.1")
    port = int(getenv("FLASK_PORT", 5000))  # noqa: PLW1508

    app.run(
        debug=debug,
        host=host,
        port=port,
    )
