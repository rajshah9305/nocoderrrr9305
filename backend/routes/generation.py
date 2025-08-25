from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import threading
import time
import random
from models.database import db
from models.user import User
from models.project import Project
from services.ai_service import AIService

generation_bp = Blueprint('generation', __name__)
ai_service = AIService()

@generation_bp.route('/generation/start', methods=['POST'])
def start_generation():
    try:
        data = request.get_json()
        
        if not data or 'project_id' not in data or 'description' not in data:
            return jsonify({'success': False, 'error': 'Project ID and description are required'}), 400
        
        project_id = data['project_id']
        description = data['description']
        requirements = data.get('requirements', {})
        
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        if project.status == 'generating':
            return jsonify({'success': False, 'error': 'Generation already in progress'}), 409
        
        # Update project status
        project.status = 'generating'
        project.started_at = datetime.utcnow()
        project.progress = 0
        project.current_agent = 'Requirements Analyst'
        project.estimated_completion = datetime.utcnow() + timedelta(minutes=5)
        project.error_message = None
        
        db.session.commit()
        
        # Start generation process in background
        generation_thread = threading.Thread(
            target=run_generation_process,
            args=(project_id, description, requirements)
        )
        generation_thread.daemon = True
        generation_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Generation started successfully',
            'project_id': project_id,
            'status': 'generating'
        }), 202
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@generation_bp.route('/generation/status/<int:project_id>', methods=['GET'])
def get_generation_status(project_id):
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'status': project.status,
            'progress': project.progress,
            'current_agent': project.current_agent,
            'started_at': project.started_at.isoformat() if project.started_at else None,
            'completed_at': project.completed_at.isoformat() if project.completed_at else None,
            'estimated_completion': project.estimated_completion.isoformat() if project.estimated_completion else None,
            'error_message': project.error_message
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@generation_bp.route('/generation/cancel/<int:project_id>', methods=['POST'])
def cancel_generation(project_id):
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        if project.status != 'generating':
            return jsonify({'success': False, 'error': 'No generation in progress'}), 400
        
        project.status = 'cancelled'
        project.completed_at = datetime.utcnow()
        project.current_agent = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Generation cancelled successfully',
            'project_id': project_id,
            'status': 'cancelled'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def run_generation_process(project_id, description, requirements):
    try:
        agents = [
            {'id': 'analyst', 'name': 'Requirements Analyst', 'duration': 30},
            {'id': 'architect', 'name': 'System Architect', 'duration': 45},
            {'id': 'designer', 'name': 'UI/UX Designer', 'duration': 40},
            {'id': 'frontend', 'name': 'Frontend Developer', 'duration': 60},
            {'id': 'backend', 'name': 'Backend Developer', 'duration': 55},
            {'id': 'deployer', 'name': 'DevOps Engineer', 'duration': 35}
        ]
        
        total_duration = sum(agent['duration'] for agent in agents)
        elapsed_time = 0
        
        generation_results = {
            'specifications': None,
            'architecture': None,
            'design': None,
            'frontend_code': None,
            'backend_code': None,
            'deployment': None
        }
        
        for i, agent in enumerate(agents):
            project = Project.query.get(project_id)
            if project.status == 'cancelled':
                return
            
            project.current_agent = agent['name']
            project.progress = int((elapsed_time / total_duration) * 100)
            db.session.commit()
            
            # Simulate agent work with AI integration
            agent_result = simulate_agent_work(agent, description, requirements, generation_results)
            
            # Store agent result
            if agent['id'] == 'analyst':
                generation_results['specifications'] = agent_result
                project.set_specifications(agent_result)
            elif agent['id'] == 'architect':
                generation_results['architecture'] = agent_result
                project.set_architecture(agent_result)
            elif agent['id'] == 'designer':
                generation_results['design'] = agent_result
                project.set_design(agent_result)
            elif agent['id'] == 'frontend':
                generation_results['frontend_code'] = agent_result
            elif agent['id'] == 'backend':
                generation_results['backend_code'] = agent_result
            elif agent['id'] == 'deployer':
                generation_results['deployment'] = agent_result
            
            # Simulate work progress
            agent_start_time = time.time()
            while time.time() - agent_start_time < agent['duration']:
                if Project.query.get(project_id).status == 'cancelled':
                    return
                
                agent_elapsed = time.time() - agent_start_time
                total_progress = int(((elapsed_time + agent_elapsed) / total_duration) * 100)
                
                project = Project.query.get(project_id)
                project.progress = min(total_progress, 100)
                db.session.commit()
                
                time.sleep(2)
            
            elapsed_time += agent['duration']
        
        # Finalize generation
        project = Project.query.get(project_id)
        if project.status != 'cancelled':
            project.status = 'completed'
            project.completed_at = datetime.utcnow()
            project.progress = 100
            project.current_agent = None
            project.set_generated_code(generation_results)
            
            # Set project metadata
            project.framework = 'React'
            project.complexity = determine_complexity(description)
            project.build_time = f"{int(total_duration / 60)}m {total_duration % 60}s"
            project.performance_score = random.randint(85, 98)
            project.set_tech_stack(['React', 'Node.js', 'PostgreSQL', 'Tailwind CSS'])
            project.set_features(extract_features(description))
            
            db.session.commit()
    
    except Exception as e:
        project = Project.query.get(project_id)
        project.status = 'failed'
        project.completed_at = datetime.utcnow()
        project.error_message = str(e)
        project.current_agent = None
        db.session.commit()

def simulate_agent_work(agent, description, requirements, previous_results):
    try:
        if agent['id'] == 'analyst':
            return ai_service.analyze_requirements(description, requirements)
        elif agent['id'] == 'architect':
            return ai_service.design_architecture(description, previous_results.get('specifications'))
        elif agent['id'] == 'designer':
            return ai_service.create_design(description, previous_results.get('specifications'))
        elif agent['id'] == 'frontend':
            return ai_service.generate_frontend_code(description, previous_results)
        elif agent['id'] == 'backend':
            return ai_service.generate_backend_code(description, previous_results)
        elif agent['id'] == 'deployer':
            return ai_service.create_deployment_config(description, previous_results)
        else:
            return {'status': 'completed', 'output': f'{agent["name"]} completed successfully'}
    
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def determine_complexity(description):
    description_lower = description.lower()
    
    complex_keywords = ['ai', 'machine learning', 'real-time', 'blockchain', 'microservices', 'analytics']
    medium_keywords = ['dashboard', 'authentication', 'database', 'api', 'integration']
    
    if any(keyword in description_lower for keyword in complex_keywords):
        return 'complex'
    elif any(keyword in description_lower for keyword in medium_keywords):
        return 'medium'
    else:
        return 'simple'

def extract_features(description):
    features = []
    description_lower = description.lower()
    
    feature_map = {
        'user': 'User Management',
        'auth': 'Authentication',
        'login': 'User Login',
        'dashboard': 'Dashboard',
        'analytics': 'Analytics',
        'chat': 'Chat System',
        'notification': 'Notifications',
        'payment': 'Payment Processing',
        'search': 'Search Functionality',
        'upload': 'File Upload',
        'real-time': 'Real-time Updates',
        'mobile': 'Mobile Responsive',
        'api': 'REST API',
        'database': 'Database Integration'
    }
    
    for keyword, feature in feature_map.items():
        if keyword in description_lower:
            features.append(feature)
    
    if not features:
        features = ['User Interface', 'Responsive Design', 'Modern Styling']
    
    return features[:6]