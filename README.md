# OPEN SOURCE CODE CHATBOT

## Goals
This chatbot allows users to ask questions about open source code and get answers from the Gemini API.

## Architecture
- **Frontend**: Next.js application (port 3000)
- **Backend**: Flask API (port 5000) - handles GitHub repo fetching and proxies chat requests
- **Agent**: Google ADK agent service (port 8080) - processes chat messages using Gemini API

## Setup

### Backend
1. Navigate to `backend/` directory
2. Copy `.env.example` to `.env` and add your GitHub token
3. Install dependencies: `uv sync`
4. Run: `python main.py`

### Agent
1. Navigate to `agent/` directory
2. Set up `.env` in `root_agent/` with your Google API key
3. Install dependencies: `uv sync`
4. Run: `python main.py`

### Frontend
1. Navigate to `frontend/` directory
2. Install dependencies: `pnpm install`
3. Run: `pnpm dev`

## API Integration

### Session Management
The application implements automatic session management following the ADK API pattern:

**Frontend Session Manager** (`frontend/src/utils/sessionManager.ts`):
- `ensureSession()`: Automatically checks if a session exists and creates one if needed
- `checkSessionExists()`: Verifies if a session is already active
- `createSession()`: Creates a new session with the agent
- `getSessionId()`: Generates consistent session IDs from repository names

**Backend Endpoints**:

1. **Check Session** (`POST /check-session`):
   - Verifies if a session exists for a given session_id
   - Returns 200 if exists, 404 if not found

2. **Create Session** (`POST /create-session`):
   - Creates a new session with the agent
   - Stores repository context in session state
   - Returns session_id for subsequent queries

3. **Chat** (`POST /chat`):
   - Accepts session_id and user_id in request
   - If no session_id provided, automatically creates one
   - Uses the ADK `/run` endpoint with proper session management
   - Builds context from GitHub repository files
   - Returns agent's response to frontend

### Flow
1. **Frontend opens chat interface**
   - Automatically calls `ensureSession()` on mount
   - Checks if session exists for the repository
   - Creates new session if needed
   - Displays connection status in UI

2. **Backend session creation**
   - Creates session via `POST /apps/root_agent/users/{user_id}/sessions/{session_id}`
   - Stores repository metadata in session state

3. **Chat messages**
   - Frontend sends messages with session_id
   - Backend forwards to agent via `POST /run` with session context
   - Agent maintains conversation history within the session
   - Backend extracts text response from events array and returns to frontend

### Benefits
- **Automatic session management**: No manual session handling required
- **Conversation persistence**: Agent remembers context across messages
- **Error recovery**: Automatically creates session if missing
- **Visual feedback**: Connection status displayed in chat UI

