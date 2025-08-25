from datetime import datetime
import json
from .database import db

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='draft')  # draft, generating, completed, failed, cancelled
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Generation metadata
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    current_agent = db.Column(db.String(100))
    progress = db.Column(db.Integer, default=0)
    estimated_completion = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Generated content (stored as JSON)
    generated_code = db.Column(db.Text)  # JSON string
    specifications = db.Column(db.Text)  # JSON string
    architecture = db.Column(db.Text)    # JSON string
    design = db.Column(db.Text)          # JSON string
    
    # Project metadata
    framework = db.Column(db.String(100), default='React')
    complexity = db.Column(db.String(50), default='medium')  # simple, medium, complex
    build_time = db.Column(db.String(50))
    performance_score = db.Column(db.Integer)
    tech_stack = db.Column(db.Text)      # JSON array as string
    features = db.Column(db.Text)        # JSON array as string
    deploy_url = db.Column(db.String(500))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chat_sessions = db.relationship('ChatSession', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        # Validate required fields
        if not kwargs.get('name') or not kwargs.get('description'):
            raise ValueError("Name and description are required")
        
        super(Project, self).__init__(**kwargs)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'user_id': self.user_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'current_agent': self.current_agent,
            'progress': self.progress,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'error_message': self.error_message,
            'framework': self.framework,
            'complexity': self.complexity,
            'build_time': self.build_time,
            'performance_score': self.performance_score,
            'deploy_url': self.deploy_url,
            'specifications': self.get_specifications(),
            'architecture': self.get_architecture(),
            'design': self.get_design(),
            'generated_code': self.get_generated_code(),
            'tech_stack': self.get_tech_stack(),
            'features': self.get_features(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    # Helper methods for JSON fields
    def set_generated_code(self, code_data):
        """Set generated code data as JSON string"""
        self.generated_code = json.dumps(code_data) if code_data else None
    
    def get_generated_code(self):
        """Get generated code data as Python object"""
        try:
            return json.loads(self.generated_code) if self.generated_code else None
        except (json.JSONDecodeError, TypeError):
            return None
    
    def set_specifications(self, specs_data):
        """Set specifications data as JSON string"""
        self.specifications = json.dumps(specs_data) if specs_data else None
    
    def get_specifications(self):
        """Get specifications data as Python object"""
        try:
            return json.loads(self.specifications) if self.specifications else None
        except (json.JSONDecodeError, TypeError):
            return None
    
    def set_architecture(self, arch_data):
        """Set architecture data as JSON string"""
        self.architecture = json.dumps(arch_data) if arch_data else None
    
    def get_architecture(self):
        """Get architecture data as Python object"""
        try:
            return json.loads(self.architecture) if self.architecture else None
        except (json.JSONDecodeError, TypeError):
            return None
    
    def set_design(self, design_data):
        """Set design data as JSON string"""
        self.design = json.dumps(design_data) if design_data else None
    
    def get_design(self):
        """Get design data as Python object"""
        try:
            return json.loads(self.design) if self.design else None
        except (json.JSONDecodeError, TypeError):
            return None
    
    def set_tech_stack(self, stack_list):
        """Set tech stack as JSON string"""
        if isinstance(stack_list, list):
            self.tech_stack = json.dumps(stack_list)
        elif isinstance(stack_list, str):
            # If it's already a string, try to parse it first
            try:
                parsed = json.loads(stack_list)
                self.tech_stack = stack_list
            except json.JSONDecodeError:
                # If it's not JSON, treat as comma-separated string
                self.tech_stack = json.dumps([item.strip() for item in stack_list.split(',')])
        else:
            self.tech_stack = json.dumps([])
    
    def get_tech_stack(self):
        """Get tech stack as list"""
        try:
            return json.loads(self.tech_stack) if self.tech_stack else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_features(self, features_list):
        """Set features as JSON string"""
        if isinstance(features_list, list):
            self.features = json.dumps(features_list)
        elif isinstance(features_list, str):
            try:
                parsed = json.loads(features_list)
                self.features = features_list
            except json.JSONDecodeError:
                self.features = json.dumps([item.strip() for item in features_list.split(',')])
        else:
            self.features = json.dumps([])
    
    def get_features(self):
        """Get features as list"""
        try:
            return json.loads(self.features) if self.features else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def __repr__(self):
        return f'<Project {self.id}: {self.name}>'


class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(50), nullable=False)  # cerebras, openai, anthropic, etc.
    key_value = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='disconnected')  # connected, disconnected, error
    last_tested = db.Column(db.DateTime)
    response_time = db.Column(db.Integer)  # in milliseconds
    error_message = db.Column(db.Text)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'service', name='unique_user_service'),)
    
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
    
    def __repr__(self):
        return f'<ApiKey {self.service} for user {self.user_id}>'


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default='New Chat')
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'message_count': len(self.messages),
            'last_message': self.messages[-1].to_dict() if self.messages else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ChatSession {self.id}: {self.title}>'


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # user, ai, system
    content = db.Column(db.Text, nullable=False)
    message_metadata = db.Column(db.Text)  # JSON string for additional data
    
    # Foreign key
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'content': self.content,
            'metadata': self.get_metadata(),
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat()
        }
    
    def set_metadata(self, metadata_data):
        """Set metadata as JSON string"""
        self.message_metadata = json.dumps(metadata_data) if metadata_data else None
    
    def get_metadata(self):
        """Get metadata as Python object"""
        try:
            return json.loads(self.message_metadata) if self.message_metadata else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def __repr__(self):
        return f'<ChatMessage {self.id}: {self.type}>'
