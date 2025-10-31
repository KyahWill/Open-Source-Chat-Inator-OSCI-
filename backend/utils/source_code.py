"""Source code fetching utilities for GitHub repositories"""
import re
import base64
import asyncio
import aiohttp
from config import GITHUB_TOKEN


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
