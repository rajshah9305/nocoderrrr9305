from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from models import db, Project
from services.ai_service import AIService
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
db.init_app(app)
ai_service = AIService()

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    
    try:
        project = Project(
            name=data['name'],
            description=data['description'],
            status='pending',
            started_at=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        return jsonify(project.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@socketio.on('start_generation')
def handle_generation(data):
    try:
        project_id = data['projectId']
        project = Project.query.get(project_id)
        
        if not project:
            raise ValueError('Project not found')
            
        # Analyze requirements
        emit('progress', {'step': 'Analyzing requirements...'})
        requirements = ai_service.analyze_requirements(project.description)
        project.set_specifications(requirements)
        
        # Design architecture
        emit('progress', {'step': 'Designing architecture...'})
        architecture = ai_service.design_architecture(project.description, requirements)
        project.set_architecture(architecture)
        
        # Generate frontend code
        emit('progress', {'step': 'Generating frontend code...'})
        frontend_code = ai_service.generate_frontend_code(project.description, {
            'requirements': requirements,
            'architecture': architecture
        })
        
        # Generate backend code
        emit('progress', {'step': 'Generating backend code...'})
        backend_code = ai_service.generate_backend_code(project.description, {
            'requirements': requirements,
            'architecture': architecture
        })
        
        # Update project status
        project.status = 'completed'
        project.completed_at = datetime.utcnow()
        project.set_generated_code({
            'frontend': frontend_code,
            'backend': backend_code
        })
        
        db.session.commit()
        
        emit('server_message', {'status': 'success', 'message': 'Generation completed'})
    except Exception as e:
        emit('server_message', {'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True)
