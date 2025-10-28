'use client';

import { useState } from 'react';
import TextEditor from '@/components/TextEditor';
import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  const [githubUrl, setGithubUrl] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [isGathering, setIsGathering] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [validationSuccess, setValidationSuccess] = useState(false);
  const [files, setFiles] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [selectedFile, setSelectedFile] = useState<any | null>(null);
  const [showChat, setShowChat] = useState(false);

  const validateGithubUrl = (url: string): boolean => {
    const githubPattern = /^https?:\/\/(www\.)?github\.com\/[\w-]+\/[\w.-]+\/?$/;
    return githubPattern.test(url);
  };

  const handleValidate = async () => {
    setValidationError('');
    setValidationSuccess(false);
    setError('');
    setFiles([]);

    if (!githubUrl.trim()) {
      setValidationError('Please enter a GitHub URL');
      return;
    }

    if (!validateGithubUrl(githubUrl)) {
      setValidationError('Invalid GitHub URL format. Expected: https://github.com/username/repository');
      return;
    }

    setIsValidating(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BACKEND_URL}/validate-github-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: githubUrl }),
      });

      const data = await response.json();

      if (!response.ok) {
        setValidationError(data.error || 'Failed to validate GitHub URL');
        return;
      }

      setValidationSuccess(true);
    } catch (err) {
      setValidationError('Failed to connect to backend. Make sure it\'s running on port 5000.');
    } finally {
      setIsValidating(false);
    }
  };

  const handleGatherFiles = async () => {
    setError('');
    setFiles([]);
    setIsGathering(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BACKEND_URL}/gather-files`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: githubUrl }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Failed to gather files');
        return;
      }

      setFiles(data.files || []);
    } catch (err) {
      setError('Failed to gather files from GitHub repository');
    } finally {
      setIsGathering(false);
    }
  };

  const handleFileClick = (file: any) => {
    setSelectedFile({
      path: file.path || file.name,
      content: file.content || ''
    });
  };

  const handleSaveFile = async (content: string) => {
    // Implement save logic here if needed
    console.log('Saving file:', selectedFile?.path, content);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 to-zinc-100 dark:from-zinc-900 dark:to-black py-12 px-4">
      <main className="max-w-4xl mx-auto">
        <div className="bg-white dark:bg-zinc-800 rounded-2xl shadow-xl p-8">
          <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
            GitHub Repository Analyzer
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400 mb-8">
            Enter a GitHub repository URL to validate and gather files
          </p>

          <div className="space-y-4">
            <div>
              <label htmlFor="github-url" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                GitHub Repository URL
              </label>
              <input
                id="github-url"
                type="text"
                value={githubUrl}
                onChange={(e) => {
                  setGithubUrl(e.target.value);
                  setValidationError('');
                  setValidationSuccess(false);
                  setFiles([]);
                }}
                placeholder="https://github.com/username/repository"
                className="w-full px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              />
            </div>

            {validationError && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-red-800 dark:text-red-200 text-sm">{validationError}</p>
              </div>
            )}

            {validationSuccess && (
              <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <p className="text-green-800 dark:text-green-200 text-sm">✓ GitHub URL validated successfully!</p>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={handleValidate}
                disabled={isValidating || !githubUrl.trim()}
                className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-300 dark:disabled:bg-zinc-700 text-white rounded-lg font-medium transition disabled:cursor-not-allowed"
              >
                {isValidating ? 'Validating...' : 'Validate URL'}
              </button>

              <button
                onClick={handleGatherFiles}
                disabled={!validationSuccess || isGathering}
                className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-zinc-300 dark:disabled:bg-zinc-700 text-white rounded-lg font-medium transition disabled:cursor-not-allowed"
              >
                {isGathering ? 'Gathering Files...' : 'Gather Files'}
              </button>
            </div>

            {validationSuccess && files.length > 0 && (
              <button
                onClick={() => setShowChat(true)}
                className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition flex items-center justify-center gap-2"
              >
                <span>💬</span>
                <span>Chat with Codebase</span>
              </button>
            )}
          </div>

          {error && (
            <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-800 dark:text-red-200 text-sm">{error}</p>
            </div>
          )}

          {files.length > 0 && (
            <div className="mt-8">
              <h2 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
                Repository Files ({files.length})
              </h2>
              <div className="bg-zinc-50 dark:bg-zinc-900 rounded-lg p-4 max-h-96 overflow-y-auto">
                <ul className="space-y-2">
                  {files.map((file, index) => (
                    <li
                      key={index}
                      onClick={() => handleFileClick(file)}
                      className="flex items-center gap-3 p-3 bg-white dark:bg-zinc-800 rounded-lg hover:shadow-md transition cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700"
                    >
                      <span className="text-zinc-400">📄</span>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
                          {file.path || file.name || 'Unknown file'}
                        </p>
                        {file.size && (
                          <p className="text-xs text-zinc-500 dark:text-zinc-400">
                            {(file.size / 1024).toFixed(2)} KB
                          </p>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        {selectedFile && (
          <TextEditor
            file={selectedFile}
            onSave={handleSaveFile}
            onClose={() => setSelectedFile(null)}
          />
        )}

        {showChat && (
          <ChatInterface
            repositoryUrl={githubUrl}
            files={files}
            onClose={() => setShowChat(false)}
          />
        )}
      </main>
    </div>
  );
}
