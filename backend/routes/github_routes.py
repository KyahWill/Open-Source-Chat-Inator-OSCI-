"""GitHub-related routes"""
from flask import Blueprint, request, jsonify

from utils.github import validate_github_url, check_url_exists
from utils.source_code import get_source_code

github_bp = Blueprint('github', __name__)


@github_bp.route('/source-code', methods=['GET'])
def fetch_source_code():
    """GET endpoint to fetch source code from a GitHub repository"""
    github_url = request.args.get('url')
    token = request.args.get('token')  # Optional token parameter
    
    if not github_url:
        return jsonify({
            'error': 'Missing URL parameter',
            'usage': 'GET /source-code?url=https://github.com/owner/repo&token=YOUR_TOKEN (optional)'
        }), 400
    
    # Validate URL format
    if not validate_github_url(github_url):
        return jsonify({
            'error': 'Invalid GitHub URL format',
            'url': github_url
        }), 400
    
    # Fetch source code with optional token
    result = get_source_code(github_url, token)
    
    # Check if there was an error
    if 'error' in result and 'files' not in result:
        return jsonify(result), 404
    
    return jsonify(result), 200


@github_bp.route('/validate-github-url', methods=['POST'])
def validate_github():
    """POST endpoint to validate GitHub URL"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({
            'error': 'Missing URL in request body',
            'valid': False
        }), 400
    
    url = data['url']
    
    # Validate URL format
    if not validate_github_url(url):
        return jsonify({
            'error': 'Invalid GitHub URL format',
            'valid': False,
            'url': url
        }), 400
    
    # Check if URL exists
    exists = check_url_exists(url)
    
    if not exists:
        return jsonify({
            'error': 'GitHub URL does not exist or is not accessible',
            'valid': False,
            'url': url
        }), 404
    
    return jsonify({
        'message': 'Valid GitHub URL',
        'valid': True,
        'url': url
    }), 200


@github_bp.route('/gather-files', methods=['POST'])
def gather_files():
    """POST endpoint to gather files from a GitHub repository"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({
            'error': 'Missing URL in request body'
        }), 400
    
    url = data['url']
    token = data.get('token')  # Optional token
    
    # Validate URL format
    if not validate_github_url(url):
        return jsonify({
            'error': 'Invalid GitHub URL format',
            'url': url
        }), 400
    
    # Fetch source code
    result = get_source_code(url, token)
    
    # Check if there was an error
    if 'error' in result and 'files' not in result:
        return jsonify(result), 404
    
    # Transform files dict into array format for frontend
    files_array = [
        {
            'path': path,
            'content': content,
            'size': len(content.encode('utf-8')) if isinstance(content, str) else 0
        }
        for path, content in result.get('files', {}).items()
    ]
    
    return jsonify({
        'repository': result.get('repository'),
        'files': files_array,
        'total_files': result.get('total_files', len(files_array))
    }), 200
