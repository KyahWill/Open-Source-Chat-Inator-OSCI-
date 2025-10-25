from flask import Flask, request, jsonify
import re
import urllib.request
import urllib.error

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
