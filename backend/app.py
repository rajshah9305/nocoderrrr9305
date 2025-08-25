import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import requests
import logging

# Load environment variables from .env file

load_dotenv()

app = Flask(**name**)
app.config[‘SECRET_KEY’] = os.environ.get(‘SECRET_KEY’, ‘default-secret-for-development’)

# Database configuration - ONLY use environment variables

database_url = os.environ.get(‘DATABASE_URL’)
if database_url and database_url.startswith(‘postgres://’):
# Heroku uses postgres:// but SQLAlchemy needs postgresql://
database_url = database_url.replace(‘postgres://’, ‘postgresql://’, 1)

app.config[‘SQLALCHEMY_DATABASE_URI’] = database_url or ‘sqlite:///default.db’
app.config[‘SQLALCHEMY_TRACK_MODIFICATIONS’] = False

# Initialize extensions

db = SQLAlchemy(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins=”*”)

# Configure logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

# Models

class Project(db.Model):
id = db.Column(db.Integer, primary_key=True)
name = db.Column(db.String(100), nullable=False)
description = db.Column(db.Text)
tech_stack = db.Column(db.String(200))
created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

```
def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'description': self.description,
        'tech_stack': self.tech_stack,
        'created_at': self.created_at.isoformat() if self.created_at else None
    }
```

# Routes

@app.route(’/’)
def home():
return jsonify({“message”: “AI App Builder API is running!”})

@app.route(’/api/generate’, methods=[‘POST’])
def generate_app():
try:
data = request.get_json()
description = data.get(‘description’, ‘’)

```
    if not description:
        return jsonify({"error": "Description is required"}), 400
    
    # Get Cerebras API key from environment
    api_key = os.environ.get('CEREBRAS_API_KEY')
    if not api_key:
        logger.error("CEREBRAS_API_KEY not found in environment variables")
        return jsonify({"error": "AI service not configured"}), 500
    
    # Call Cerebras API
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "model": "llama3.1-70b",
        "messages": [
            {
                "role": "system", 
                "content": "You are an expert web developer. Generate complete, working code for web applications based on user descriptions."
            },
            {
                "role": "user", 
                "content": f"Create a complete web application: {description}"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    response = requests.post(
        'https://api.cerebras.ai/v1/chat/completions',
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        ai_response = response.json()
        generated_code = ai_response['choices'][0]['message']['content']
        
        # Save to database
        project = Project(
            name=data.get('name', 'Generated App'),
            description=description,
            tech_stack=data.get('tech_stack', 'HTML, CSS, JavaScript')
        )
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            "code": generated_code,
            "project_id": project.id,
            "message": "Application generated successfully!"
        })
    else:
        logger.error(f"Cerebras API error: {response.status_code} - {response.text}")
        return jsonify({"error": "Failed to generate application"}), 500
        
except Exception as e:
    logger.error(f"Error generating app: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500
```

@app.route(’/api/projects’, methods=[‘GET’])
def get_projects():
try:
projects = Project.query.order_by(Project.created_at.desc()).all()
return jsonify([project.to_dict() for project in projects])
except Exception as e:
logger.error(f”Error fetching projects: {str(e)}”)
return jsonify({“error”: “Failed to fetch projects”}), 500

# Socket.IO events

@socketio.on(‘connect’)
def handle_connect():
logger.info(‘Client connected’)
emit(‘status’, {‘message’: ‘Connected to AI App Builder’})

@socketio.on(‘disconnect’)
def handle_disconnect():
logger.info(‘Client disconnected’)

# Create tables

with app.app_context():
try:
db.create_all()
logger.info(“Database tables created successfully”)
except Exception as e:
logger.error(f”Error creating database tables: {str(e)}”)

if **name** == ‘**main**’:
port = int(os.environ.get(‘PORT’, 5000))
socketio.run(app, host=‘0.0.0.0’, port=port, debug=False)
