"""Configuration module for backend service"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GitHub token from environment variable
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# Agent service URL
AGENT_SERVICE_URL = os.environ.get('AGENT_SERVICE_URL', 'http://localhost:8080')
