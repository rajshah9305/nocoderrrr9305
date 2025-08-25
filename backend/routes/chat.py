from flask import Blueprint, request, jsonify
from datetime import datetime
import json
from models.database import db
from models.user import User
from models.project import ChatSession, ChatMessage
from services.ai_service import AIService

chat_bp = Blueprint('chat', __name__)
ai_service = AIService()

@chat_bp.route('/chat/sessions', methods=['GET'])
def get_chat_sessions():
    try:
        user = User.query.first()
        if not user:
            user = User(name="Demo User", email="demo@aiappbuilder.com")
            db.session.add(user)
            db.session.commit()
        
        sessions = ChatSession.query.filter_by(user_id=user.id).order_by(ChatSession.updated_at.desc()).all()
        
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/chat/sessions', methods=['POST'])
def create_chat_session():
    try:
        data = request.get_json()
        
        user = User.query.first()
        if not user:
            user = User(name="Demo User", email="demo@aiappbuilder.com")
            db.session.add(user)
            db.session.commit()
        
        session = ChatSession(
            title=data.get('title', 'New Chat'),
            project_id=data.get('project_id'),
            user_id=user.id
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session': session.to_dict(),
            'message': 'Chat session created successfully'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/chat/sessions/<int:session_id>/messages', methods=['GET'])
def get_chat_messages(session_id):
    try:
        session = ChatSession.query.get(session_id)
        
        if not session:
            return jsonify({'success': False, 'error': 'Chat session not found'}), 404
        
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at.asc()).all()
        
        return jsonify({
            'success': True,
            'messages': [message.to_dict() for message in messages],
            'session': session.to_dict()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/chat/sessions/<int:session_id>/messages', methods=['POST'])
def send_chat_message(session_id):
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'success': False, 'error': 'Message content is required'}), 400
        
        session = ChatSession.query.get(session_id)
        
        if not session:
            return jsonify({'success': False, 'error': 'Chat session not found'}), 404
        
        user_content = data['content']
        
        # Save user message
        user_message = ChatMessage(
            type='user',
            content=user_content,
            session_id=session_id
        )
        
        db.session.add(user_message)
        db.session.commit()
        
        # Generate AI response
        try:
            ai_response = generate_ai_response(user_content, session)
            
            # Save AI message
            ai_message = ChatMessage(
                type='ai',
                content=ai_response['content'],
                session_id=session_id,
                message_metadata=json.dumps(ai_response.get('metadata', {}))
            )
            
            db.session.add(ai_message)
            
            # Update session title if it's the first message
            if session.title == 'New Chat' and len(session.messages) <= 2:
                session.title = generate_session_title(user_content)
            
            session.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'user_message': user_message.to_dict(),
                'ai_message': ai_message.to_dict(),
                'session': session.to_dict()
            })
        
        except Exception as ai_error:
            db.session.commit()
            
            return jsonify({
                'success': False,
                'user_message': user_message.to_dict(),
                'error': f'AI response failed: {str(ai_error)}'
            }), 500
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/chat/sessions/<int:session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    try:
        session = ChatSession.query.get(session_id)
        
        if not session:
            return jsonify({'success': False, 'error': 'Chat session not found'}), 404
        
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Chat session deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/chat/quick-help', methods=['POST'])
def quick_help():
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'success': False, 'error': 'Question is required'}), 400
        
        question = data['question']
        response = get_quick_help_response(question)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': response,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_ai_response(user_message, session):
    try:
        recent_messages = ChatMessage.query.filter_by(session_id=session.id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(10).all()
        
        context = {
            'session_id': session.id,
            'project_id': session.project_id,
            'conversation_history': [
                {
                    'type': msg.type,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat()
                }
                for msg in reversed(recent_messages)
            ]
        }
        
        prompt = build_ai_chat_prompt(user_message, context)
        ai_response_text = get_ai_chat_response(prompt)
        
        return {
            'content': ai_response_text,
            'metadata': {
                'model': 'ai-assistant',
                'timestamp': datetime.utcnow().isoformat(),
                'context_used': len(context['conversation_history'])
            }
        }
    
    except Exception as e:
        return {
            'content': "I apologize, but I'm having trouble processing your request right now. Please try again later.",
            'metadata': {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        }

def build_ai_chat_prompt(user_message, context):
    system_prompt = """
You are an AI assistant for the AI App Builder Pro platform. You help users with:

1. Understanding how to use the platform
2. Providing guidance on app development
3. Explaining technical concepts
4. Troubleshooting issues
5. Suggesting best practices

You are knowledgeable, helpful, and concise. Always provide practical advice and actionable suggestions.
    """
    
    conversation_context = ""
    if context['conversation_history']:
        conversation_context = "\n\nConversation History:\n"
        for msg in context['conversation_history'][-5:]:
            conversation_context += f"{msg['type'].title()}: {msg['content']}\n"
    
    prompt = f"{system_prompt}{conversation_context}\n\nUser: {user_message}\n\nAssistant:"
    
    return prompt

def get_ai_chat_response(prompt):
    try:
        response = ai_service._call_ai_service(prompt, "chat_response")
        
        if isinstance(response, str):
            return response
        else:
            return "I understand your question. Let me help you with that. Could you provide more specific details about what you're trying to accomplish?"
    
    except Exception as e:
        return "I'm currently experiencing some technical difficulties. Please try again in a moment."

def generate_session_title(first_message):
    message_lower = first_message.lower()
    
    if 'help' in message_lower or 'how' in message_lower:
        return "Help & Guidance"
    elif 'build' in message_lower or 'create' in message_lower:
        return "App Building"
    elif 'deploy' in message_lower:
        return "Deployment Help"
    elif 'error' in message_lower or 'problem' in message_lower:
        return "Troubleshooting"
    elif 'api' in message_lower:
        return "API Configuration"
    else:
        words = first_message.split()[:4]
        return ' '.join(words) + ('...' if len(first_message.split()) > 4 else '')

def get_quick_help_response(question):
    question_lower = question.lower()
    
    if 'how to start' in question_lower or 'getting started' in question_lower:
        return "To get started: 1) Describe your app idea in the Builder tab, 2) Click 'Generate App' to start the AI generation process, 3) Monitor progress in real-time, 4) Review and deploy your generated app."
    
    elif 'api key' in question_lower:
        return "To configure API keys: 1) Click the settings icon in the top right, 2) Enter your API keys for AI services (Cerebras, OpenAI, etc.), 3) Test the connection, 4) Save your configuration."
    
    elif 'deploy' in question_lower:
        return "Your app will be automatically deployed once generation is complete. You can also manually deploy using the deployment options in your project settings."
    
    elif 'progress' in question_lower or 'status' in question_lower:
        return "You can monitor generation progress in real-time on the Builder tab. The progress bar shows which AI agent is currently working and the overall completion percentage."
    
    elif 'error' in question_lower or 'problem' in question_lower:
        return "If you encounter errors: 1) Check your API key configuration, 2) Ensure your description is clear and detailed, 3) Try regenerating the app, 4) Contact support if issues persist."
    
    else:
        return "I'm here to help! You can ask me about getting started, configuring API keys, monitoring progress, deployment, or troubleshooting issues. What specific topic would you like help with?"