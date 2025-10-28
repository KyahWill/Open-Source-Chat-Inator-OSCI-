'use client';

import { useState, useEffect } from 'react';

interface TextEditorProps {
  file: {
    path: string;
    content?: string;
  };
  onSave?: (content: string) => void;
  onClose?: () => void;
}

export default function TextEditor({ file, onSave, onClose }: TextEditorProps) {
  const [content, setContent] = useState(file.content || '');
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setContent(file.content || '');
    setHasChanges(false);
  }, [file.path, file.content]);

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    setHasChanges(newContent !== (file.content || ''));
  };

  const handleSave = async () => {
    if (!onSave) return;
    
    setIsSaving(true);
    try {
      await onSave(content);
      setHasChanges(false);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-zinc-800 rounded-xl shadow-2xl w-full max-w-6xl h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-zinc-200 dark:border-zinc-700">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📝</span>
            <div>
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                {file.path}
              </h2>
              {hasChanges && (
                <p className="text-xs text-amber-600 dark:text-amber-400">
                  Unsaved changes
                </p>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {onSave && (
              <button
                onClick={handleSave}
                disabled={!hasChanges || isSaving}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-300 dark:disabled:bg-zinc-700 text-white text-sm rounded-lg font-medium transition disabled:cursor-not-allowed"
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            )}
            {onClose && (
              <button
                onClick={onClose}
                className="px-4 py-2 bg-zinc-200 hover:bg-zinc-300 dark:bg-zinc-700 dark:hover:bg-zinc-600 text-zinc-900 dark:text-zinc-100 text-sm rounded-lg font-medium transition"
              >
                Close
              </button>
            )}
          </div>
        </div>

        {/* Editor */}
        <div className="flex-1 overflow-hidden">
          <textarea
            value={content}
            onChange={(e) => handleContentChange(e.target.value)}
            className="w-full h-full p-4 bg-zinc-50 dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 font-mono text-sm resize-none focus:outline-none"
            spellCheck={false}
            placeholder="File content will appear here..."
          />
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-3 border-t border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-900">
          <div className="text-xs text-zinc-500 dark:text-zinc-400">
            {content.split('\n').length} lines • {content.length} characters
          </div>
          <div className="text-xs text-zinc-500 dark:text-zinc-400">
            Press Cmd+S to save
          </div>
        </div>
      </div>
    </div>
  );
}
