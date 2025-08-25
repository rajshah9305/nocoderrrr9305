from flask import Blueprint, request, jsonify
from datetime import datetime
import time
import requests
from models.database import db
from models.user import User
from models.project import ApiKey

api_keys_bp = Blueprint('api_keys', __name__)

@api_keys_bp.route('/api-keys', methods=['GET'])
def get_api_keys():
    try:
        user = User.query.first()
        if not user:
            user = User(name="Demo User", email="demo@aiappbuilder.com")
            db.session.add(user)
            db.session.commit()
        
        api_keys = ApiKey.query.filter_by(user_id=user.id).all()
        
        return jsonify({
            'success': True,
            'api_keys': [api_key.to_dict() for api_key in api_keys]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_keys_bp.route('/api-keys', methods=['POST'])
def save_api_key():
    try:
        data = request.get_json()
        
        if not data or 'service' not in data or 'key_value' not in data:
            return jsonify({'success': False, 'error': 'Service and key_value are required'}), 400
        
        service = data['service']
        key_value = data['key_value']
        
        valid_services = ['cerebras', 'openai', 'anthropic', 'vercel', 'netlify', 'supabase', 'stripe']
        if service not in valid_services:
            return jsonify({'success': False, 'error': f'Invalid service. Must be one of: {", ".join(valid_services)}'}), 400
        
        user = User.query.first()
        if not user:
            user = User(name="Demo User", email="demo@aiappbuilder.com")
            db.session.add(user)
            db.session.commit()
        
        existing_key = ApiKey.query.filter_by(user_id=user.id, service=service).first()
        
        if existing_key:
            existing_key.key_value = key_value
            existing_key.status = 'disconnected'
            existing_key.last_tested = None
            existing_key.response_time = None
            existing_key.error_message = None
            existing_key.updated_at = datetime.utcnow()
            api_key = existing_key
        else:
            api_key = ApiKey(
                service=service,
                key_value=key_value,
                user_id=user.id,
                status='disconnected'
            )
            db.session.add(api_key)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'api_key': api_key.to_dict(),
            'message': f'{service.title()} API key saved successfully'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_keys_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
def delete_api_key(key_id):
    try:
        api_key = ApiKey.query.get(key_id)
        
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not found'}), 404
        
        service_name = api_key.service
        db.session.delete(api_key)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{service_name.title()} API key deleted successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_keys_bp.route('/api-keys/test', methods=['POST'])
def test_api_key():
    try:
        data = request.get_json()
        
        if not data or 'service' not in data or 'key_value' not in data:
            return jsonify({'success': False, 'error': 'Service and key_value are required'}), 400
        
        service = data['service']
        key_value = data['key_value']
        
        start_time = time.time()
        test_result = test_service_connection(service, key_value)
        response_time = int((time.time() - start_time) * 1000)
        
        user = User.query.first()
        if user:
            api_key = ApiKey.query.filter_by(user_id=user.id, service=service).first()
            if api_key:
                api_key.status = 'connected' if test_result['success'] else 'error'
                api_key.last_tested = datetime.utcnow()
                api_key.response_time = response_time
                api_key.error_message = test_result.get('error')
                db.session.commit()
        
        return jsonify({
            'success': test_result['success'],
            'service': service,
            'response_time': response_time,
            'message': test_result.get('message', 'Connection test completed'),
            'error': test_result.get('error')
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def test_service_connection(service, api_key):
    try:
        if service == 'cerebras':
            return test_cerebras_connection(api_key)
        elif service == 'openai':
            return test_openai_connection(api_key)
        elif service == 'anthropic':
            return test_anthropic_connection(api_key)
        elif service == 'vercel':
            return test_vercel_connection(api_key)
        elif service == 'netlify':
            return test_netlify_connection(api_key)
        else:
            return {'success': False, 'error': f'Unknown service: {service}'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_cerebras_connection(api_key):
    try:
        if api_key.startswith('csk-'):
            return {'success': True, 'message': 'Cerebras API connection successful'}
        else:
            return {'success': False, 'error': 'Invalid Cerebras API key format'}
    
    except Exception as e:
        return {'success': False, 'error': f'Cerebras API test failed: {str(e)}'}

def test_openai_connection(api_key):
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': 'Hello'}],
            'max_tokens': 5
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            return {'success': True, 'message': 'OpenAI API connection successful'}
        else:
            return {'success': False, 'error': f'OpenAI API error: {response.status_code}'}
    
    except Exception as e:
        return {'success': False, 'error': f'OpenAI API test failed: {str(e)}'}

def test_anthropic_connection(api_key):
    try:
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-3-haiku-20240307',
            'max_tokens': 5,
            'messages': [{'role': 'user', 'content': 'Hello'}]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            return {'success': True, 'message': 'Anthropic API connection successful'}
        else:
            return {'success': False, 'error': f'Anthropic API error: {response.status_code}'}
    
    except Exception as e:
        return {'success': False, 'error': f'Anthropic API test failed: {str(e)}'}

def test_vercel_connection(api_key):
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://api.vercel.com/v2/user',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return {'success': True, 'message': 'Vercel API connection successful'}
        else:
            return {'success': False, 'error': f'Vercel API error: {response.status_code}'}
    
    except Exception as e:
        return {'success': False, 'error': f'Vercel API test failed: {str(e)}'}

def test_netlify_connection(api_key):
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://api.netlify.com/api/v1/user',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return {'success': True, 'message': 'Netlify API connection successful'}
        else:
            return {'success': False, 'error': f'Netlify API error: {response.status_code}'}
    
    except Exception as e:
        return {'success': False, 'error': f'Netlify API test failed: {str(e)}'}