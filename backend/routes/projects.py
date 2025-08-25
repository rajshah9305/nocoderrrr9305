from flask import Blueprint, request, jsonify
from datetime import datetime
from models.database import db
from models.user import User
from models.project import Project

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET'])
def get_projects():
    try:
        user = User.query.first()
        if not user:
            user = User(name="Demo User", email="demo@aiappbuilder.com")
            db.session.add(user)
            db.session.commit()
        
        projects = Project.query.filter_by(user_id=user.id).order_by(Project.updated_at.desc()).all()
        
        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects],
            'total': len(projects)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects', methods=['POST'])
def create_project():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'description' not in data:
            return jsonify({'success': False, 'error': 'Name and description are required'}), 400
        
        user = User.query.first()
        if not user:
            user = User(name="Demo User", email="demo@aiappbuilder.com")
            db.session.add(user)
            db.session.commit()
        
        project = Project(
            name=data['name'],
            description=data['description'],
            user_id=user.id,
            status='draft',
            framework=data.get('framework', 'React'),
            complexity=data.get('complexity', 'medium')
        )
        
        if 'tech_stack' in data:
            project.set_tech_stack(data['tech_stack'])
        
        if 'features' in data:
            project.set_features(data['features'])
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'message': 'Project created successfully'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        return jsonify({'success': True, 'project': project.to_dict()})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        # Update basic fields
        for field in ['name', 'description', 'status', 'framework', 'complexity', 'current_agent', 'progress', 'error_message']:
            if field in data:
                setattr(project, field, data[field])
        
        # Update generated content
        if 'generated_code' in data:
            project.set_generated_code(data['generated_code'])
        if 'specifications' in data:
            project.set_specifications(data['specifications'])
        if 'architecture' in data:
            project.set_architecture(data['architecture'])
        if 'design' in data:
            project.set_design(data['design'])
        
        # Update metadata
        for field in ['tech_stack', 'features']:
            if field in data:
                getattr(project, f'set_{field}')(data[field])
        
        for field in ['deploy_url', 'build_time', 'performance_score']:
            if field in data:
                setattr(project, field, data[field])
        
        # Update timestamps
        if data.get('status') == 'generating' and not project.started_at:
            project.started_at = datetime.utcnow()
        elif data.get('status') in ['completed', 'failed', 'cancelled'] and not project.completed_at:
            project.completed_at = datetime.utcnow()
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'message': 'Project updated successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Project deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/stats', methods=['GET'])
def get_project_stats():
    try:
        user = User.query.first()
        if not user:
            return jsonify({
                'success': True,
                'stats': {'total_projects': 0, 'deployed': 0, 'building': 0, 'total_views': 0}
            })
        
        total_projects = Project.query.filter_by(user_id=user.id).count()
        deployed = Project.query.filter_by(user_id=user.id, status='completed').count()
        building = Project.query.filter_by(user_id=user.id, status='generating').count()
        total_views = total_projects * 150 + deployed * 500
        
        return jsonify({
            'success': True,
            'stats': {
                'total_projects': total_projects,
                'deployed': deployed,
                'building': building,
                'total_views': total_views
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500