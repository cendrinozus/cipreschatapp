from app import db
from datetime import datetime
import bcrypt

class User(db.Model):
    __tablename__ = "users"
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)
    role       = db.Column(db.Enum("admin", "user"), default="user", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active  = db.Column(db.Boolean, default=True)

    sessions = db.relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, plain):
        self.password = bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    def check_password(self, plain):
        return bcrypt.checkpw(plain.encode(), self.password.encode())

    def to_dict(self):
        return {"id": self.id, "username": self.username,
                "email": self.email, "role": self.role,
                "created_at": self.created_at.isoformat()}


class ChatSession(db.Model):
    __tablename__ = "chat_sessions"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title      = db.Column(db.String(200), default="Nouvelle conversation")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user     = db.relationship("User", back_populates="sessions")
    messages = db.relationship("Message", back_populates="session", cascade="all, delete-orphan",
                               order_by="Message.created_at")

    def to_dict(self):
        return {"id": self.id, "title": self.title,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat()}


class Message(db.Model):
    __tablename__ = "messages"
    id         = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("chat_sessions.id"), nullable=False)
    role       = db.Column(db.Enum("user", "assistant"), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    sources    = db.Column(db.JSON, nullable=True)   # [{file, chunk_id, score}]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship("ChatSession", back_populates="messages")

    def to_dict(self):
        return {"id": self.id, "role": self.role, "content": self.content,
                "sources": self.sources, "created_at": self.created_at.isoformat()}
