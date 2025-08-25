# backend/app.py
import os
from dotenv import load_dotenv
from . import create_socketio_app, socketio

load_dotenv()  # loads .env in dev

app = create_socketio_app()

if __name__ == "__main__":
    # Use eventlet or gevent for websockets if available
    use_reloader = os.getenv("FLASK_RELOAD", "1") == "1"
    try:
        import eventlet
        eventlet.monkey_patch()
        socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=use_reloader)
    except Exception:
        socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=use_reloader)
