"""Agent service-related routes"""
from flask import Blueprint, request, jsonify

from utils.agent import check_session_exists, create_agent_session, send_chat_message

agent_bp = Blueprint('agent', __name__)


@agent_bp.route('/check-session', methods=['POST'])
def check_session():
    """POST endpoint to check if a session exists"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Missing request body'
        }), 400
    
    user_id = data.get('user_id', 'default_user')
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({
            'error': 'Missing session_id'
        }), 400
    
    exists, status_code, error = check_session_exists(user_id, session_id)
    
    if error:
        return jsonify({'error': error}), status_code
    
    if exists:
        return jsonify({
            'exists': True,
            'session_id': session_id
        }), 200
    else:
        return jsonify({
            'exists': False,
            'session_id': session_id
        }), 404


@agent_bp.route('/create-session', methods=['POST'])
def create_session():
    """POST endpoint to create a new agent session"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Missing request body'
        }), 400
    
    repository = data.get('repository', '')
    user_id = data.get('user_id', 'default_user')
    session_id = data.get('session_id', f'session_{repository.replace("/", "_")}')
    
    success, response_data, status_code = create_agent_session(user_id, session_id, repository)
    
    return jsonify(response_data), status_code


@agent_bp.route('/chat', methods=['POST'])
def chat():
    """POST endpoint to chat with the codebase using the agent"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({
            'error': 'Missing message in request body'
        }), 400
    
    message = data['message']
    repository = data.get('repository', '')
    files = data.get('files', [])
    user_id = data.get('user_id', 'default_user')
    session_id = data.get('session_id')
    
    # If no session_id provided, create one based on repository
    if not session_id:
        session_id = f'session_{repository.replace("/", "_")}' if repository else 'default_session'
        
        # Try to create the session first
        create_agent_session(user_id, session_id, repository)
    
    success, response_data, status_code = send_chat_message(
        user_id, session_id, message, repository, files
    )
    
    return jsonify(response_data), status_code
