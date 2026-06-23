from flask import Blueprint, request, jsonify
from app import db
from app.models.models import User, ChatSession, Message
from app.routes.auth import admin_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.get("/users")
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])

@admin_bp.post("/users")
@admin_required
def create_user():
    data = request.get_json()
    if User.query.filter_by(email=data.get("email")).first():
        return jsonify({"error": "Email déjà utilisé"}), 409
    user = User(
        username=data["username"],
        email=data["email"],
        role=data.get("role", "user"),
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@admin_bp.patch("/users/<int:uid>")
@admin_required
def update_user(uid):
    user = User.query.get_or_404(uid)
    data = request.get_json()
    if "role"      in data: user.role      = data["role"]
    if "is_active" in data: user.is_active = data["is_active"]
    if "password"  in data: user.set_password(data["password"])
    db.session.commit()
    return jsonify(user.to_dict())

@admin_bp.delete("/users/<int:uid>")
@admin_required
def delete_user(uid):
    user = User.query.get_or_404(uid)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Utilisateur supprimé"})

@admin_bp.get("/stats")
@admin_required
def stats():
    return jsonify({
        "users":    User.query.count(),
        "sessions": ChatSession.query.count(),
        "messages": Message.query.count(),
    })
