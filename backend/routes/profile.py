from flask import Blueprint, jsonify, request

from extensions import db
from models import Profile, User
from services.profile_utils import parse_fixed_expenses, serialize_fixed_expenses, fixed_expenses_total


bp = Blueprint("profile", __name__, url_prefix="/api/profile")


def _get_or_create_user(user_id: int) -> User:
    user = User.query.get(user_id)
    if not user:
        user = User(id=user_id, name="Demo User")
        db.session.add(user)
        db.session.flush()
    return user


def _profile_to_dict(p: Profile) -> dict:
    fixed_items = parse_fixed_expenses(p.fixed_expenses)
    return {
        "id": p.id,
        "income": float(p.income or 0),
        "fixed_expenses": fixed_items,
        "fixed_expenses_total": fixed_expenses_total(fixed_items),
        "monthly_limit": float(p.monthly_limit or 0),
        "savings_goal": float(p.savings_goal or 0),
        "currency": p.currency or "INR",
        "profile_picture_url": p.profile_picture_url,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


@bp.route("", methods=["GET"])
def get_profile():
    user_id = int(request.args.get("user_id", "1"))
    _get_or_create_user(user_id)
    p = Profile.query.get(user_id)
    if not p:
        # return a sensible default shell profile
        return jsonify(
            {
                "id": user_id,
                "income": 0.0,
                "fixed_expenses": [],
                "fixed_expenses_total": 0.0,
                "monthly_limit": 0.0,
                "savings_goal": 0.0,
                "currency": "INR",
                "profile_picture_url": None,
                "created_at": None,
                "updated_at": None,
            }
        )
    return jsonify(_profile_to_dict(p))


def _write_profile_from_payload(user_id: int, payload: dict) -> Profile:
    _get_or_create_user(user_id)
    p = Profile.query.get(user_id)
    if not p:
        p = Profile(id=user_id)
        db.session.add(p)

    if "income" in payload:
        try:
            p.income = float(payload["income"])
        except Exception:
            pass
    if "monthly_limit" in payload:
        try:
            p.monthly_limit = float(payload["monthly_limit"])
        except Exception:
            pass
    if "savings_goal" in payload:
        try:
            p.savings_goal = float(payload["savings_goal"])
        except Exception:
            pass
    if "currency" in payload:
        p.currency = str(payload["currency"])[:10]
    if "profile_picture_url" in payload:
        url = payload.get("profile_picture_url")
        p.profile_picture_url = str(url)[:255] if url else None
    if "fixed_expenses" in payload:
        p.fixed_expenses = serialize_fixed_expenses(payload.get("fixed_expenses"))

    db.session.commit()
    return p


@bp.route("", methods=["POST"])
def create_profile():
    user_id = int(request.args.get("user_id", "1"))
    data = request.get_json(silent=True) or {}
    p = _write_profile_from_payload(user_id, data)
    return jsonify(_profile_to_dict(p)), 201


@bp.route("", methods=["PUT"])
def update_profile():
    user_id = int(request.args.get("user_id", "1"))
    data = request.get_json(silent=True) or {}
    p = _write_profile_from_payload(user_id, data)
    return jsonify(_profile_to_dict(p))

