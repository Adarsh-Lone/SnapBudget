<<<<<<< HEAD
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import config

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -----------------------
# DATABASE MODEL
# -----------------------
class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    account_id = db.Column(db.Integer)
    source_type = db.Column(db.String(50))
    raw_text = db.Column(db.Text)

    merchant = db.Column(db.String(255))
    amount = db.Column(db.Float)
    currency = db.Column(db.String(10))
    transaction_date = db.Column(db.Date)

    category = db.Column(db.String(100))
    is_recurring = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

# -----------------------
# HOME
# -----------------------
@app.route("/")
def home():
    return {"message": "SnapBudget Backend Running 🚀"}

# -----------------------
# GET TRANSACTIONS
# -----------------------
@app.route("/api/transactions")
def get_transactions():

    user_id = request.args.get("user_id", type=int)

    transactions = Transaction.query.filter_by(user_id=user_id).all()

    data = [
        {
            "merchant": t.merchant,
            "amount": float(t.amount),
            "category": t.category,
            "date": t.transaction_date.strftime("%Y-%m-%d") if t.transaction_date else None
        }
        for t in transactions
    ]

    return jsonify({"transactions": data})

# -----------------------
# SUMMARY ANALYTICS
# -----------------------
@app.route("/api/analytics/summary")
def summary():

    user_id = request.args.get("user_id", type=int)

    transactions = Transaction.query.filter_by(user_id=user_id).all()

    total = sum(float(t.amount) for t in transactions)
    count = len(transactions)

    avg = total / count if count else 0

    return jsonify({
        "total_spend": total,
        "avg_spend": avg,
        "transactions": count
    })

# -----------------------
# PARSE SMS
# -----------------------
@app.route("/api/transactions/parse-sms", methods=["POST"])
def parse_sms():

    data = request.json
    text = data.get("text")
    user_id = data.get("user_id")

    # demo parsing
    new_tx = Transaction(
        user_id=user_id,
        merchant="SMS Merchant",
        amount=500,
        category="Other"
    )

    db.session.add(new_tx)
    db.session.commit()

    return {"status": "added"}

# -----------------------
# RECEIPT UPLOAD
# -----------------------
@app.route("/api/transactions/upload-receipt", methods=["POST"])
def upload_receipt():

    file = request.files.get("file")

    if not file:
        return {"error": "No file uploaded"}, 400

    new_tx = Transaction(
        user_id=1,
        merchant="Receipt Store",
        amount=100,
        category="Receipt"
    )

    db.session.add(new_tx)
    db.session.commit()

    return {"status": "receipt processed"}

# -----------------------
# TEST DB
# -----------------------
@app.route("/testdb")
def testdb():
    tx = Transaction.query.all()
    return {"rows": len(tx)}

# -----------------------
# RUN SERVER
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
=======
import os

from flask import Flask, jsonify, send_from_directory
from sqlalchemy import text  # <

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

    # Optional: serve the React SPA build for direct navigation to
    # /profile, /analytics, /alerts, /insights when deployed as a single app.
    frontend_build = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
    )

    def _serve_spa():
        index_path = os.path.join(frontend_build, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(frontend_build, "index.html")
        # dev mode: frontend is typically served by react-scripts
        return jsonify(
            {
                "message": "Frontend build not found. Run the React dev server in /frontend, or build it via `npm run build`."
            }
        )

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path: str):
        # never intercept API routes
        if path.startswith("api/"):
            return jsonify({"error": "Not found"}), 404

        # serve static assets if present
        static_path = os.path.join(frontend_build, path)
        if path and os.path.exists(static_path) and os.path.isfile(static_path):
            return send_from_directory(frontend_build, path)

        # otherwise serve SPA entrypoint
        return _serve_spa()

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # Do not call db.create_all(); we rely on schema.sql
       db.session.execute(text("SELECT 1"))
    app.run(host="0.0.0.0", port=5000, debug=True)

>>>>>>> e8bc353 (Updated backend, frontend, analytics, alerts, and insights features)
