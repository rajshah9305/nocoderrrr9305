from datetime import datetime
import json
from .database import db

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='draft')
    
    # Generation metadata
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    current_agent = db.Column(db.String(100))
    progress = db.Column(db.Integer, default=0)
    estimated_completion = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Generated content
    generated_code = db.Column(db.Text)
    specifications = db.Column(db.Text)
    architecture = db.Column(db.Text)
    design = db.Column(db.Text)
    
    # Project metadata
    framework = db.Column(db.String(100))
    complexity = db.Column(db.String(50))
    build_time = db.Column(db.String(50))
    performance_score = db.Column(db.Integer)
    tech_stack = db.Column(db.Text)
    features = db.Column(db.Text)
    deploy_url = db.Column(db.String(500))
    
    # Relations
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'current_agent': self.current_agent,
            'progress': self.progress,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'error_message': self.error_message,
            'generated_code': json.loads(self.generated_code) if self.generated_code else None,
            'specifications': json.loads(self.specifications) if self.specifications else None,
            'architecture': json.loads(self.architecture) if self.architecture else None,
            'design': json.loads(self.design) if self.design else None,
            'framework': self.framework,
            'complexity': self.complexity,
            'build_time': self.build_time,
            'performance_score': self.performance_score,
            'tech_stack': json.loads(self.tech_stack) if self.tech_stack else [],
            'features': json.loads(self.features) if self.features else [],
            'deploy_url': self.deploy_url,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def set_generated_code(self, code_data):
        self.generated_code = json.dumps(code_data) if code_data else None
    
    def set_specifications(self, specs_data):
        self.specifications = json.dumps(specs_data) if specs_data else None
    
    def set_architecture(self, arch_data):
        self.architecture = json.dumps(arch_data) if arch_data else None
    
    def set_design(self, design_data):
        self.design = json.dumps(design_data) if design_data else None
    
    def set_tech_stack(self, tech_list):
        self.tech_stack = json.dumps(tech_list) if tech_list else None
    
    def set_features(self, features_list):
        self.features = json.dumps(features_list) if features_list else None

class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(100), nullable=False)
    key_value = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='disconnected')
    
    # Testing metadata
    last_tested = db.Column(db.DateTime)
    response_time = db.Column(db.Integer)
    error_message = db.Column(db.Text)
    
    # Relations
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'service': self.service,
            'status': self.status,
            'last_tested': self.last_tested.isoformat() if self.last_tested else None,
            'response_time': self.response_time,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    # Relations
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'message_count': len(self.messages),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_metadata = db.Column(db.Text)
    
    # Relations
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'content': self.content,
            'metadata': json.loads(self.message_metadata) if self.message_metadata else None,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat()
        }