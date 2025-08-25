# backend/routes/api.py
from flask import Blueprint, jsonify, request

api_bp = Blueprint("api", __name__)

@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

@api_bp.route("/generate", methods=["POST"])
def generate():
    payload = request.get_json(force=True) or {}
    idea = payload.get("idea", "Hello World App")
    # TODO: wire up your agents; return stub for now
    return jsonify(projectName=f"{idea}", steps=["plan","scaffold","code","deploy"]), 200
