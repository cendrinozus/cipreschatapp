from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.routes.auth      import auth_bp
    from app.routes.chat      import chat_bp
    from app.routes.documents import documents_bp
    from app.routes.admin     import admin_bp

    app.register_blueprint(auth_bp,      url_prefix="/api/auth")
    app.register_blueprint(chat_bp,      url_prefix="/api/chat")
    app.register_blueprint(documents_bp, url_prefix="/api/documents")
    app.register_blueprint(admin_bp,     url_prefix="/api/admin")

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    from app.models.models import User
    if not User.query.filter_by(email="admin@lacipres.org").first():
        admin = User(username="admin", email="admin@lacipres.org", role="admin")
        admin.set_password("1234")
        db.session.add(admin)
        db.session.commit()
