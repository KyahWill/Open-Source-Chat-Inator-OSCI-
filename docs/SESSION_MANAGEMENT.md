# Session Management Implementation

## Overview
This document describes the automatic session management system implemented for the GitHub Repository Analyzer chatbot.

## Architecture

### Frontend (`frontend/src/utils/sessionManager.ts`)

The session manager provides a clean API for managing agent sessions:

```typescript
// Ensure a session exists (creates if needed)
const session = await ensureSession(repository, userId);

// Check if session exists
const exists = await checkSessionExists(repository, userId);

// Create a new session
const session = await createSession(repository, userId);

// Get session ID without creating
const sessionId = getSessionId(repository);
```

### Backend Endpoints

#### 1. Check Session (`POST /check-session`)
```json
Request:
{
  "session_id": "session_owner_repo",
  "user_id": "default_user"
}

Response (200 if exists):
{
  "exists": true,
  "session_id": "session_owner_repo"
}

Response (404 if not found):
{
  "exists": false,
  "session_id": "session_owner_repo"
}
```

#### 2. Create Session (`POST /create-session`)
```json
Request:
{
  "repository": "owner/repo",
  "user_id": "default_user",
  "session_id": "session_owner_repo"
}

Response:
{
  "session_id": "session_owner_repo",
  "user_id": "default_user",
  "repository": "owner/repo",
  "message": "Session created successfully"
}
```

#### 3. Chat (`POST /chat`)
```json
Request:
{
  "message": "What does this code do?",
  "repository": "owner/repo",
  "files": [...],
  "session_id": "session_owner_repo",
  "user_id": "default_user"
}

Response:
{
  "response": "This code implements...",
  "repository": "owner/repo",
  "files_count": 42,
  "session_id": "session_owner_repo",
  "user_id": "default_user"
}
```

## Integration with Google ADK

The backend properly integrates with the Google Agent Development Kit (ADK) API:

1. **Session Creation**: `POST /apps/root_agent/users/{user_id}/sessions/{session_id}`
   - Creates a session in the ADK agent service
   - Stores initial state with repository information

2. **Query Execution**: `POST /run`
   - Sends messages to the agent with session context
   - Agent maintains conversation history
   - Returns events array with response

## User Experience

### Chat Interface Behavior

1. **On Mount**:
   - Automatically calls `ensureSession()`
   - Shows "✓ Connected" badge when session is ready
   - Shows "⚠ Session Error" badge if session fails

2. **Sending Messages**:
   - Checks for active session before sending
   - Creates session automatically if missing
   - Includes session_id in all chat requests

3. **Visual Feedback**:
   - Connection status badge in header
   - Error messages in chat if session fails
   - Loading states during session creation

## Error Handling

### Frontend
- Retries session creation if initial attempt fails
- Shows user-friendly error messages
- Continues to work with fallback session creation

### Backend
- Validates session existence before queries
- Creates session automatically if missing
- Returns detailed error messages for debugging

## Session ID Format

Session IDs are generated consistently from repository names:

```
Repository: https://github.com/owner/repo
Session ID: session_owner_repo

Repository: owner/repo
Session ID: session_owner_repo
```

This ensures:
- Same repository always gets same session ID
- Sessions persist across page refreshes (if backend maintains them)
- Easy to debug and trace sessions

## Testing

### Test Session Creation
```bash
curl -X POST http://localhost:5000/create-session \
  -H "Content-Type: application/json" \
  -d '{"repository": "test/repo", "user_id": "test_user"}'
```

### Test Session Check
```bash
curl -X POST http://localhost:5000/check-session \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session_test_repo", "user_id": "test_user"}'
```

### Test Chat with Session
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "repository": "test/repo",
    "session_id": "session_test_repo",
    "user_id": "test_user",
    "files": []
  }'
```

## Benefits

1. **Automatic**: No manual session management required
2. **Persistent**: Conversation context maintained across messages
3. **Resilient**: Automatically recovers from session errors
4. **Transparent**: Visual feedback for session status
5. **Consistent**: Same repository always uses same session
6. **Debuggable**: Clear session IDs and error messages
