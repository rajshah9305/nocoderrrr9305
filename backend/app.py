import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import requests
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-for-development')

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Heroku compatibility: postgres:// -> postgresql://
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///ai_app_builder.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, resources={
    r"/api/*": {"origins": os.environ.get('CORS_ORIGINS', '*').split(',')},
    r"/socket.io/*": {"origins": os.environ.get('CORS_ORIGINS', '*').split(',')}
})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

# Import models (after db initialization)
from models.user import User
from models.project import Project, ApiKey, ChatSession, ChatMessage

# Import routes
from routes.projects import projects_bp
from routes.api_keys import api_keys_bp
from routes.chat import chat_bp
from routes.generation import generation_bp

# Register blueprints
app.register_blueprint(projects_bp, url_prefix='/api')
app.register_blueprint(api_keys_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')
app.register_blueprint(generation_bp, url_prefix='/api')

# Root routes
@app.route('/')
def home():
    return jsonify({
        "message": "AI App Builder Pro API",
        "version": "2.0.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/health')
def health_check():
    try:
        # Database connectivity check
        db.session.execute('SELECT 1')
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 503

# Legacy generate route for backward compatibility
@app.route('/api/generate', methods=['POST'])
def legacy_generate():
    try:
        data = request.get_json()
        description = data.get('description', '')
        
        if not description:
            return jsonify({"error": "Description is required"}), 400
        
        # Create a new project
        user = User.query.first()
        if not user:
            user = User(name="Demo User", email="demo@aiappbuilder.com")
            db.session.add(user)
            db.session.commit()
        
        project = Project(
            name=data.get('name', 'Generated App'),
            description=description,
            user_id=user.id,
            framework=data.get('framework', 'React'),
            complexity='medium'
        )
        
        if 'tech_stack' in data:
            project.set_tech_stack(data['tech_stack'])
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            "project_id": project.id,
            "message": "Project created successfully. Use /api/generation/start to begin generation.",
            "redirect_to": f"/api/generation/start"
        })
        
    except Exception as e:
        logger.error(f"Error in legacy generate: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    logger.info(f'Client connected: {request.sid}')
    emit('status', {
        'message': 'Connected to AI App Builder Pro',
        'timestamp': datetime.utcnow().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f'Client disconnected: {request.sid}')

@socketio.on('join_project')
def handle_join_project(data):
    project_id = data.get('project_id')
    if project_id:
        join_room(f'project_{project_id}')
        emit('joined_project', {'project_id': project_id})

@socketio.on('start_generation')
def handle_start_generation(data):
    project_id = data.get('project_id')
    description = data.get('description', '')
    
    if not project_id or not description:
        emit('generation_error', {'error': 'Project ID and description required'})
        return
    
    # Emit to the generation service
    emit('generation_started', {
        'project_id': project_id,
        'message': f'Generation started for project {project_id}'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "The requested resource was not found",
        "status_code": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    db.session.rollback()
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "status_code": 500
    }), 500

# Initialize database
def init_db():
    """Initialize database tables"""
    try:
        with app.app_context():
            db.create_all()
            
            # Create demo user if it doesn't exist
            if not User.query.first():
                demo_user = User(
                    name="Demo User",
                    email="demo@aiappbuilder.com"
                )
                db.session.add(demo_user)
                db.session.commit()
                logger.info("Demo user created")
            
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting AI App Builder Pro on port {port}")
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=debug,
        use_reloader=False  # Prevents double initialization
    )
