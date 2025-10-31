"""Flask backend service for GitHub repository analysis"""
from flask import Flask
from flask_cors import CORS

from routes.github_routes import github_bp
from routes.agent_routes import agent_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(github_bp)
app.register_blueprint(agent_bp)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
