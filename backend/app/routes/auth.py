from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.models import User
from functools import wraps

auth_bp = Blueprint("auth", __name__)

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        uid  = int(get_jwt_identity())
        user = User.query.get(uid)
        if not user or user.role != "admin":
            return jsonify({"error": "Accès réservé aux administrateurs"}), 403
        return fn(*args, **kwargs)
    return wrapper

@auth_bp.post("/login")
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not user.check_password(data.get("password", "")):
        return jsonify({"error": "Identifiants invalides"}), 401
    if not user.is_active:
        return jsonify({"error": "Compte désactivé"}), 403
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()})

@auth_bp.post("/register")
def register():
    data = request.get_json()
    if User.query.filter_by(email=data.get("email")).first():
        return jsonify({"error": "Email déjà utilisé"}), 409
    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 201

@auth_bp.get("/me")
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404
    return jsonify(user.to_dict())
