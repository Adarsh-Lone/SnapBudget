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

    with app.app_context():
        db.session.execute(text("SELECT 1"))

    app.run(host="0.0.0.0", port=5000, debug=True)