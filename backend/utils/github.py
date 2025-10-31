"""GitHub URL validation and checking utilities"""
import re
import urllib.request
import urllib.error


def validate_github_url(url):
    """Validate if the URL is a valid GitHub URL"""
    github_pattern = r'^https?://github\.com/[\w\-\.]+/[\w\-\.]+/?.*'
    return re.match(github_pattern, url) is not None


def check_url_exists(url):
    """Check if the GitHub URL returns a valid response"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except (urllib.error.HTTPError, urllib.error.URLError, Exception):
        return False
