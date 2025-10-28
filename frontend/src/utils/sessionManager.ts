/**
 * Session Manager for Agent Communication
 * Handles session creation and management with the backend agent service
 */

const BACKEND_URL = 'https://cloud-run-hackathon-backend-816885386955.asia-southeast1.run.app';

interface SessionInfo {
  session_id: string;
  user_id: string;
  repository: string;
}

/**
 * Check if a session exists for the given repository
 */
export async function checkSessionExists(
  repository: string,
  userId: string = 'default_user'
): Promise<boolean> {
  const sessionId = generateSessionId(repository);

  try {
    // Try to get the session from the agent service via backend
    const response = await fetch(`${BACKEND_URL}/check-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        user_id: userId,
      }),
    });

    return response.ok;
  } catch (error) {
    console.error('Error checking session:', error);
    return false;
  }
}

/**
 * Create a new session for the repository
 */
export async function createSession(
  repository: string,
  userId: string = 'default_user'
): Promise<SessionInfo | null> {
  const sessionId = generateSessionId(repository);

  try {
    const response = await fetch(`${BACKEND_URL}/create-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        repository,
        user_id: userId,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.statusText}`);
    }

    const data = await response.json();
    return {
      session_id: data.session_id || sessionId,
      user_id: data.user_id || userId,
      repository: data.repository || repository,
    };
  } catch (error) {
    console.error('Error creating session:', error);
    return null;
  }
}

/**
 * Ensure a session exists, creating one if necessary
 */
export async function ensureSession(
  repository: string,
  userId: string = 'default_user'
): Promise<SessionInfo | null> {
  // Check if session already exists
  const exists = await checkSessionExists(repository, userId);

  if (exists) {
    console.log('Session already exists for repository:', repository);
    return {
      session_id: generateSessionId(repository),
      user_id: userId,
      repository,
    };
  }

  // Create new session
  console.log('Creating new session for repository:', repository);
  return await createSession(repository, userId);
}

/**
 * Generate a consistent session ID from repository name
 */
function generateSessionId(repository: string): string {
  // Remove protocol and domain if full URL is provided
  const repoName = repository
    .replace(/^https?:\/\/(www\.)?github\.com\//, '')
    .replace(/\/$/, '');

  // Convert to session ID format
  return `session_${repoName.replace(/\//g, '_')}`;
}

/**
 * Get session ID for a repository without creating it
 */
export function getSessionId(repository: string): string {
  return generateSessionId(repository);
}
