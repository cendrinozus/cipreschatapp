from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.models import ChatSession, Message
from app.services.rag import ask

chat_bp = Blueprint("chat", __name__)

# ── Sessions ──────────────────────────────────────────────────────────────────

@chat_bp.get("/sessions")
@jwt_required()
def list_sessions():
    uid      = int(get_jwt_identity())
    sessions = ChatSession.query.filter_by(user_id=uid).order_by(
        ChatSession.updated_at.desc()).all()
    return jsonify([s.to_dict() for s in sessions])

@chat_bp.post("/sessions")
@jwt_required()
def create_session():
    uid     = int(get_jwt_identity())
    session = ChatSession(user_id=uid)
    db.session.add(session)
    db.session.commit()
    return jsonify(session.to_dict()), 201

@chat_bp.delete("/sessions/<int:session_id>")
@jwt_required()
def delete_session(session_id):
    uid     = int(get_jwt_identity())
    session = ChatSession.query.filter_by(id=session_id, user_id=uid).first_or_404()
    db.session.delete(session)
    db.session.commit()
    return jsonify({"message": "Session supprimée"})

# ── Messages ──────────────────────────────────────────────────────────────────

@chat_bp.get("/sessions/<int:session_id>/messages")
@jwt_required()
def get_messages(session_id):
    uid     = int(get_jwt_identity())
    session = ChatSession.query.filter_by(id=session_id, user_id=uid).first_or_404()
    return jsonify([m.to_dict() for m in session.messages])

@chat_bp.post("/sessions/<int:session_id>/ask")
@jwt_required()
def ask_question(session_id):
    uid     = int(get_jwt_identity())
    session = ChatSession.query.filter_by(id=session_id, user_id=uid).first_or_404()
    data    = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question vide"}), 400

    # Historique pour le contexte conversationnel
    history = [{"role": m.role, "content": m.content} for m in session.messages[-12:]]

    # Sauvegarde message utilisateur
    user_msg = Message(session_id=session.id, role="user", content=question)
    db.session.add(user_msg)

    # Mise à jour du titre de session si c'est le premier message
    if not session.messages:
        session.title = question[:80] + ("…" if len(question) > 80 else "")

    # Pipeline RAG
    result = ask(question, history=history)

    # Sauvegarde réponse assistant
    assistant_msg = Message(
        session_id=session.id,
        role="assistant",
        content=result["answer"],
        sources=result["sources"],
    )
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({
        "answer":     result["answer"],
        "sources":    result["sources"],
        "cited":      result["cited"],
        "api_calls":  result.get("api_calls", []),
        "message_id": assistant_msg.id,
    })
