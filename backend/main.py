from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import urllib.request
import urllib.error
import json
import base64
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# GitHub token from environment variable
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

def validate_github_url(url):
    """Validate if the URL is a valid GitHub URL"""
    github_pattern = r'^https?://github\.com/[\w\-\.]+/[\w\-\.]+/?.*$'
    return re.match(github_pattern, url) is not None

def check_url_exists(url):
    """Check if the GitHub URL returns a valid response"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except urllib.error.HTTPError as e:
        return False
    except urllib.error.URLError as e:
        return False
    except Exception as e:
        return False

async def fetch_file_content(session, owner, repo, file_path, auth_token):
    """Fetch a single file's content asynchronously"""
    file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/vnd.github.v3+json'
    }
    if auth_token:
        headers['Authorization'] = f'token {auth_token}'
    
    try:
        async with session.get(file_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
            file_data = await response.json()
            
            # Decode base64 content
            if 'content' in file_data:
                content = base64.b64decode(file_data['content']).decode('utf-8', errors='ignore')
                return file_path, content
            return file_path, 'No content available'
    
    except Exception as e:
        return file_path, f'Error fetching file: {str(e)}'

async def get_source_code_async(github_url, token=None):
    """
    Fetch all source code from a GitHub repository asynchronously
    
    Args:
        github_url: GitHub repository URL (e.g., https://github.com/owner/repo)
        token: Optional GitHub personal access token for authentication
    
    Returns:
        dict: Dictionary containing files with their paths and content
    """
    # Parse GitHub URL to extract owner and repo
    pattern = r'https?://github\.com/([\w\-\.]+)/([\w\-\.]+)/?.*'
    match = re.match(pattern, github_url)
    
    if not match:
        return {'error': 'Invalid GitHub URL'}
    
    owner, repo = match.groups()
    repo = repo.rstrip('.git')  # Remove .git suffix if present
    
    # Use provided token or fall back to environment variable
    auth_token = token or GITHUB_TOKEN
    
    # Build headers
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Add authentication if token is available
    if auth_token:
        headers['Authorization'] = f'token {auth_token}'
    
    async with aiohttp.ClientSession() as session:
        # Try main branch first
        for branch in ['main', 'master']:
            api_url = f'https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1'
            
            try:
                async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        continue
                    
                    tree_data = await response.json()
                    
                    if 'tree' not in tree_data:
                        continue
                    
                    # Get all file paths
                    file_items = [item for item in tree_data['tree'] if item['type'] == 'blob']
                    
                    # Fetch all files concurrently
                    tasks = [
                        fetch_file_content(session, owner, repo, item['path'], auth_token)
                        for item in file_items
                    ]
                    
                    results = await asyncio.gather(*tasks)
                    files = dict(results)
                    
                    return {
                        'repository': f'{owner}/{repo}',
                        'files': files,
                        'total_files': len(files)
                    }
            
            except Exception as e:
                if branch == 'master':  # Last attempt failed
                    return {'error': f'Error fetching source code: {str(e)}'}
                continue
        
        return {'error': 'Repository not found or inaccessible'}

def get_source_code(github_url, token=None):
    """Synchronous wrapper for async get_source_code_async"""
    return asyncio.run(get_source_code_async(github_url, token))

@app.route('/source-code', methods=['GET'])
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

@app.route('/validate-github-url', methods=['POST'])
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

@app.route('/gather-files', methods=['POST'])
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

@app.route('/chat', methods=['POST'])
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
    
    # TODO: Integrate with your agent service
    # For now, return a placeholder response
    # You'll need to call your agent API at http://localhost:8080
    
    try:
        # Example: Forward to agent service
        # agent_response = requests.post(
        #     'http://localhost:8080/api/agent/chat',
        #     json={'message': message, 'context': {'repository': repository, 'files': files}}
        # )
        # return jsonify({'response': agent_response.json()['response']}), 200
        
        # Placeholder response
        response_text = f"I received your question: '{message}'. I'm analyzing the codebase from {repository} with {len(files)} files. This is a placeholder response - integrate with your agent service for actual AI responses."
        
        return jsonify({
            'response': response_text,
            'repository': repository,
            'files_count': len(files)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Error processing chat request: {str(e)}'
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)