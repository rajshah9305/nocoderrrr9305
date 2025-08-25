from datetime import datetime
import json
from . import db

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
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, description, status='draft'):
        if not name or not description:
            raise ValueError("Name and description are required")
        self.name = name
        self.description = description
        self.status = status
    
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
            'specifications': json.loads(self.specifications) if self.specifications else None,
            'architecture': json.loads(self.architecture) if self.architecture else None,
            'generated_code': json.loads(self.generated_code) if self.generated_code else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def set_generated_code(self, code_data):
        self.generated_code = json.dumps(code_data) if code_data else None
    
    def set_specifications(self, specs_data):
        self.specifications = json.dumps(specs_data) if specs_data else None
    
    def set_architecture(self, arch_data):
        self.architecture = json.dumps(arch_data) if arch_data else None
