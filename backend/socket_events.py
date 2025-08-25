# backend/socket_events.py
from . import socketio
from flask import request

@socketio.on("connect")
def on_connect():
    socketio.emit("server_message", {"event": "connected"}, to=request.sid)

@socketio.on("start_generation")
def start_generation(data):
    # TODO: hook your multi-agent pipeline and emit progress
    for step in ["planning", "scaffolding", "coding", "deploying", "done"]:
        socketio.emit("progress", {"step": step})
