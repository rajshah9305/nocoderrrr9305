import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from models.database import db
from models.user import User
from routes.projects import projects_bp
from routes.generation import generation_bp
from routes.api_keys import api_keys_bp
from routes.chat import chat_bp

def create_app():
    app = Flask(__name__, static_folder='../dist')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Database configuration
    database_path = os.path.join(os.path.dirname(__file__), 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CORS configuration
    CORS(app, origins=[
        'http://localhost:5173',
        'http://localhost:3000',
        'https://*.vercel.app',
        os.getenv('FRONTEND_URL', '')
    ], supports_credentials=True)
    
    # SocketIO for real-time communication
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(projects_bp, url_prefix='/api')
    app.register_blueprint(generation_bp, url_prefix='/api')
    app.register_blueprint(api_keys_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Create demo user if not exists
        if not User.query.first():
            demo_user = User(name="Demo User", email="demo@aiappbuilder.com")
            db.session.add(demo_user)
            db.session.commit()
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'AI App Builder Pro Backend',
            'version': '1.0.0'
        })
    
    # Serve React app
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        try:
            if path != "" and app.static_folder and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            elif app.static_folder and os.path.exists(os.path.join(app.static_folder, 'index.html')):
                return send_from_directory(app.static_folder, 'index.html')
            else:
                return jsonify({'message': 'Frontend not built. Run: npm run build'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # SocketIO event handlers
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    @socketio.on('generation_progress')
    def handle_generation_progress(data):
        socketio.emit('generation_update', data, broadcast=True)
    
    app.socketio = socketio
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    print(f"Starting server on port {port}")
    try:
        app.socketio.run(app, host='127.0.0.1', port=port, debug=True, allow_unsafe_werkzeug=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {port} is in use, trying port {port + 1}")
            app.socketio.run(app, host='127.0.0.1', port=port + 1, debug=True, allow_unsafe_werkzeug=True)
        else:
            raise e
# At the bottom of your backend/app.py file, add this:

# For Vercel serverless deployment

app = create_app()  # Assuming you have a create_app function

if **name** == ‘**main**’:
socketio.run(app, debug=True, port=5000)
else:
# Export for Vercel
application = app
