"""Agent service communication utilities"""
import requests
from config import AGENT_SERVICE_URL


def check_session_exists(user_id, session_id):
    """
    Check if a session exists in the agent service
    
    Args:
        user_id: User identifier
        session_id: Session identifier
    
    Returns:
        tuple: (exists: bool, status_code: int, error: str or None)
    """
    try:
        session_url = f"{AGENT_SERVICE_URL}/apps/root_agent/users/{user_id}/sessions/{session_id}"
        
        session_response = requests.get(session_url, timeout=10)
        
        if session_response.status_code == 200:
            return True, 200, None
        else:
            return False, 404, None
        
    except requests.exceptions.ConnectionError:
        return False, 503, 'Could not connect to agent service. Make sure it is running on port 8080.'
    except Exception as e:
        return False, 500, f'Error checking session: {str(e)}'


def create_agent_session(user_id, session_id, repository=''):
    """
    Create a new agent session
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        repository: Repository name/identifier
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int)
    """
    try:
        session_url = f"{AGENT_SERVICE_URL}/apps/root_agent/users/{user_id}/sessions/{session_id}"
        session_payload = {
            "state": {
                "repository": repository,
                "initialized": True
            }
        }
        
        session_response = requests.post(
            session_url,
            json=session_payload,
            timeout=10
        )
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            return True, {
                'session_id': session_data.get('id', session_id),
                'user_id': user_id,
                'repository': repository,
                'message': 'Session created successfully'
            }, 200
        else:
            return False, {
                'error': f'Failed to create session: {session_response.status_code}',
                'details': session_response.text
            }, 500
        
    except requests.exceptions.ConnectionError:
        return False, {
            'error': 'Could not connect to agent service. Make sure it is running on port 8080.'
        }, 503
    except Exception as e:
        return False, {
            'error': f'Error creating session: {str(e)}'
        }, 500


def send_chat_message(user_id, session_id, message, repository='', files=None):
    """
    Send a chat message to the agent service
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        message: User message
        repository: Repository name/identifier
        files: List of file information dicts
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int)
    """
    if files is None:
        files = []
    
    try:
        # Build context from repository and files
        context = f"Repository: {repository}\n\n"
        if files:
            context += f"Analyzing {len(files)} files from the codebase.\n\n"
            # Include file paths and snippets for context
            for file_info in files[:10]:  # Limit to first 10 files to avoid token limits
                path = file_info.get('path', '')
                content = file_info.get('content', '')
                context += f"File: {path}\n"
                # Include first 500 chars of each file as context
                if content and len(content) > 500:
                    context += f"{content[:500]}...\n\n"
                elif content:
                    context += f"{content}\n\n"
        
        # Combine context with user message
        full_message = f"{context}\nUser Question: {message}"
        
        # Call the agent service using the correct ADK endpoint with the session
        agent_url = f"{AGENT_SERVICE_URL}/run"
        agent_payload = {
            "app_name": "root_agent",
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": full_message}]
            }
        }
        
        agent_response = requests.post(
            agent_url,
            json=agent_payload,
            timeout=30
        )
        
        if agent_response.status_code == 200:
            events = agent_response.json()
            # Extract the agent's text response from the events
            response_text = ""
            for event in events:
                if 'content' in event and 'parts' in event['content']:
                    for part in event['content']['parts']:
                        if 'text' in part:
                            response_text += part['text']
            
            if not response_text:
                response_text = "No response from agent"
            
            return True, {
                'response': response_text,
                'repository': repository,
                'files_count': len(files),
                'session_id': session_id,
                'user_id': user_id
            }, 200
        else:
            return False, {
                'error': f'Agent service returned status {agent_response.status_code}',
                'details': agent_response.text
            }, 500
        
    except requests.exceptions.ConnectionError:
        return False, {
            'error': 'Could not connect to agent service. Make sure it is running on port 8080.'
        }, 503
    except requests.exceptions.Timeout:
        return False, {
            'error': 'Agent service request timed out'
        }, 504
    except Exception as e:
        return False, {
            'error': f'Error processing chat request: {str(e)}'
        }, 500
