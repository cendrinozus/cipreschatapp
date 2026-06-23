import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.routes.auth import admin_required
from app.services.ingestor import ingest_file, remove_file
from werkzeug.utils import secure_filename

documents_bp = Blueprint("documents", __name__)

def allowed(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]

@documents_bp.get("/")
@jwt_required()
def list_documents():
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    files = []
    for fname in os.listdir(folder):
        path = os.path.join(folder, fname)
        files.append({
            "filename": fname,
            "size_kb":  round(os.path.getsize(path) / 1024, 1),
            "modified": os.path.getmtime(path),
        })
    files.sort(key=lambda f: f["modified"], reverse=True)
    return jsonify(files)

@documents_bp.post("/upload")
@admin_required
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400
    file = request.files["file"]
    if not file.filename or not allowed(file.filename):
        return jsonify({"error": "Format de fichier non autorisé"}), 400

    folder   = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(folder, filename)
    file.save(filepath)

    try:
        result = ingest_file(filepath, filename)
        return jsonify({"message": "Document indexé avec succès", **result}), 201
    except Exception as e:
        os.remove(filepath)
        return jsonify({"error": str(e)}), 500

@documents_bp.delete("/<filename>")
@admin_required
def delete_document(filename):
    try:
        remove_file(filename)
        return jsonify({"message": f"{filename} supprimé et désindexé"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
