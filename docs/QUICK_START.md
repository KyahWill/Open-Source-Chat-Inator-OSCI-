# Quick Start Guide

## Running the Application

### 1. Start the Agent Service
```bash
cd agent
python main.py
```
The agent will run on `http://localhost:8080`

### 2. Start the Backend
```bash
cd backend
python main.py
```
The backend will run on `http://localhost:5000`

### 3. Start the Frontend
```bash
cd frontend
pnpm dev
```
The frontend will run on `http://localhost:3000`

## Using the Application

### Step 1: Enter GitHub URL
1. Open `http://localhost:3000` in your browser
2. Enter a GitHub repository URL (e.g., `https://github.com/owner/repo`)
3. Click "Validate URL"

### Step 2: Gather Files
1. After validation succeeds, click "Gather Files"
2. Wait for the files to be fetched from GitHub
3. You'll see a list of all files in the repository

### Step 3: Start Chatting
1. Click "💬 Chat with Codebase"
2. Wait for the session to initialize (you'll see "✓ Connected")
3. Ask questions about the codebase!

## Example Questions

### General Questions
- "What does this repository do?"
- "Explain the overall architecture"
- "What are the main components?"

### Code-Specific Questions
- "How does the authentication work?"
- "Show me how to use the API"
- "What dependencies does this project use?"

### File-Specific Questions
- "Explain the main.py file"
- "What does the ChatInterface component do?"
- "How is the session management implemented?"

## Features

### Markdown Responses
The agent responds with formatted markdown including:
- **Code blocks** with syntax highlighting
- **Tables** for structured data
- **Lists** for organized information
- **Links** to relevant resources

### Session Management
- Sessions are created automatically
- Conversation context is maintained
- Connection status is shown in the UI

### Error Handling
- Automatic retry on connection errors
- Clear error messages
- Graceful degradation

## Troubleshooting

### Agent Not Connecting
**Error**: "Could not connect to agent service"

**Solution**:
1. Make sure agent is running on port 8080
2. Check agent logs for errors
3. Verify Google API key is set in `agent/root_agent/.env`

### Backend Not Responding
**Error**: "Failed to connect to backend"

**Solution**:
1. Make sure backend is running on port 5000
2. Check backend logs for errors
3. Verify GitHub token is set in `backend/.env`

### Session Creation Failed
**Error**: "⚠ Session Error"

**Solution**:
1. Refresh the page
2. Try closing and reopening the chat
3. Check that agent service is running

### No Files Loaded
**Error**: "Failed to gather files"

**Solution**:
1. Verify the GitHub URL is correct
2. Check if the repository is public
3. Ensure GitHub token has proper permissions

## Tips

### Best Practices
1. **Be Specific**: Ask detailed questions for better answers
2. **Use Context**: Reference specific files or functions
3. **Follow Up**: Ask clarifying questions if needed
4. **Check Markdown**: Responses use markdown formatting

### Performance
- First message may take longer (session creation)
- Subsequent messages are faster (session reuse)
- Large repositories may take time to analyze

### Limitations
- Only analyzes files fetched from GitHub
- Limited to first 10 files for context (to avoid token limits)
- Session persists only while services are running

## Advanced Usage

### Custom Session IDs
Sessions are automatically created based on repository name:
```
Repository: owner/repo
Session ID: session_owner_repo
```

### Multiple Repositories
You can chat with different repositories by:
1. Closing the current chat
2. Entering a new GitHub URL
3. Starting a new chat (new session created)

### API Direct Access

You can also use the API directly:

**Create Session:**
```bash
curl -X POST http://localhost:5000/create-session \
  -H "Content-Type: application/json" \
  -d '{"repository": "owner/repo"}'
```

**Send Chat Message:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does this code do?",
    "repository": "owner/repo",
    "session_id": "session_owner_repo",
    "files": []
  }'
```

## Documentation

- [Session Management](SESSION_MANAGEMENT.md) - Detailed session flow
- [Markdown Support](MARKDOWN_SUPPORT.md) - Markdown features
- [API Integration](../README.md#api-integration) - Backend/Agent integration

## Support

For issues or questions:
1. Check the logs (agent, backend, frontend)
2. Review the documentation
3. Verify all services are running
4. Check environment variables are set correctly
