import os

from flask import Flask, jsonify, send_from_directory
from sqlalchemy import text

from config import config
from extensions import init_extensions, db
from routes import transactions_bp, analytics_bp, profile_bp, advanced_analytics_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    init_extensions(app)

    # Ensure database tables exist (works for both SQLite fallback and MySQL).
    with app.app_context():
        try:
            db.create_all()
        except Exception as exc:  # noqa: BLE001
            # Don't prevent the app from starting if DB is misconfigured;
            # individual requests will surface errors instead.
            print("WARNING: db.create_all() failed:", repr(exc))

    app.register_blueprint(transactions_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(advanced_analytics_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    frontend_build = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
    )

    def _serve_spa():
        index_path = os.path.join(frontend_build, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(frontend_build, "index.html")

        return jsonify({
            "message": "Frontend build not found. Run React dev server or build frontend."
        })

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path: str):

        if path.startswith("api/"):
            return jsonify({"error": "Not found"}), 404

        static_path = os.path.join(frontend_build, path)

        if path and os.path.exists(static_path) and os.path.isfile(static_path):
            return send_from_directory(frontend_build, path)

        return _serve_spa()

    return app


if __name__ == "__main__":
    app = create_app()

    # Try a lightweight DB connectivity check
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
        except Exception as exc:
            print("WARNING: Database connectivity test failed:", repr(exc))

    app.run(host="0.0.0.0", port=5000, debug=True)