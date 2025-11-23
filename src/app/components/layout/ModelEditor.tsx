/**
 * Model Editor Layout
 *
 * Main layout component for the Model Editor UI
 * Three-panel layout: Navigator | Main Canvas | Agent Panel
 */

import React, { useState } from 'react';
import {
  Entity,
  Algorithm,
  Workflow,
  EntitiesSpec,
  AlgorithmsSpec,
  WorkflowsSpec,
  PendingChange,
} from '../../types/specs';

interface ModelEditorProps {
  entities: EntitiesSpec;
  algorithms: AlgorithmsSpec;
  workflows: WorkflowsSpec;
  pendingChanges: PendingChange[];
  onSaveEntity: (entity: Entity) => void;
  onSaveAlgorithm: (algorithm: Algorithm) => void;
  onSaveWorkflow: (workflow: Workflow) => void;
}

type EditorMode = 'entities' | 'algorithms' | 'workflows';

export const ModelEditor: React.FC<ModelEditorProps> = ({
  entities,
  algorithms,
  workflows,
  pendingChanges,
  onSaveEntity,
  onSaveAlgorithm,
  onSaveWorkflow,
}) => {
  const [mode, setMode] = useState<EditorMode>('entities');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [agentPanelOpen, setAgentPanelOpen] = useState(true);
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [chatInput, setChatInput] = useState('');

  const getSelectedItem = () => {
    switch (mode) {
      case 'entities':
        return entities.entities.find((e) => e.id === selectedId);
      case 'algorithms':
        return algorithms.algorithms.find((a) => a.id === selectedId);
      case 'workflows':
        return workflows.workflows.find((w) => w.id === selectedId);
    }
  };

  const getItemsForMode = () => {
    switch (mode) {
      case 'entities':
        return entities.entities.map((e) => ({ id: e.id, name: e.name }));
      case 'algorithms':
        return algorithms.algorithms.map((a) => ({ id: a.id, name: a.name }));
      case 'workflows':
        return workflows.workflows.map((w) => ({ id: w.id, name: w.name }));
    }
  };

  const getPendingForItem = (id: string) => {
    return pendingChanges.find((c) => c.id === id);
  };

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    // Add user message
    setChatMessages([...chatMessages, { role: 'user', content: chatInput }]);

    // TODO: Send to Claude and get response
    // For now, simulate a response
    setTimeout(() => {
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `I can help you with "${chatInput}". What would you like to know?`,
        },
      ]);
    }, 500);

    setChatInput('');
  };

  return (
    <div className="model-editor">
      {/* Header */}
      <header className="editor-header">
        <div className="header-left">
          <h1>Model Editor</h1>
          <div className="mode-tabs">
            <button
              className={mode === 'entities' ? 'active' : ''}
              onClick={() => setMode('entities')}
            >
              Entities ({entities.entities.length})
            </button>
            <button
              className={mode === 'algorithms' ? 'active' : ''}
              onClick={() => setMode('algorithms')}
            >
              Algorithms ({algorithms.algorithms.length})
            </button>
            <button
              className={mode === 'workflows' ? 'active' : ''}
              onClick={() => setMode('workflows')}
            >
              Workflows ({workflows.workflows.length})
            </button>
          </div>
        </div>
        <div className="header-right">
          <button className="btn-icon" title="Generate code">
            ⚙️
          </button>
          <button className="btn-icon" title="GitHub status">
            📊
          </button>
          <button
            className="btn-icon"
            onClick={() => setAgentPanelOpen(!agentPanelOpen)}
            title="Toggle agent panel"
          >
            🤖
          </button>
        </div>
      </header>

      <div className="editor-body">
        {/* Navigator Panel */}
        <aside className="navigator-panel">
          <div className="navigator-header">
            <input type="text" placeholder="Search..." className="search-input" />
            <button className="btn-add-new">+</button>
          </div>

          <div className="item-list">
            {getItemsForMode().map((item) => {
              const pending = getPendingForItem(item.id);
              return (
                <div
                  key={item.id}
                  className={`item-row ${selectedId === item.id ? 'selected' : ''}`}
                  onClick={() => setSelectedId(item.id)}
                >
                  <span className="item-name">{item.name}</span>
                  {pending && (
                    <span className={`status-dot ${pending.status}`} title={pending.status} />
                  )}
                </div>
              );
            })}
          </div>

          {/* Pending Changes Summary */}
          {pendingChanges.length > 0 && (
            <div className="pending-summary">
              <h4>Pending Changes ({pendingChanges.length})</h4>
              {pendingChanges.slice(0, 3).map((change) => (
                <div key={change.id} className="pending-item">
                  <span>{change.action}</span>
                  <span className={`status ${change.status}`}>{change.status}</span>
                </div>
              ))}
            </div>
          )}
        </aside>

        {/* Main Canvas */}
        <main className="main-canvas">
          {selectedId ? (
            <div className="editor-content">
              {/* Editor component would go here based on mode */}
              <div className="placeholder-editor">
                <h2>{getSelectedItem()?.name || 'Select an item'}</h2>
                <p>Editor for {mode} will render here</p>
                {/* In a real implementation, render EntityEditor, AlgorithmEditor, or WorkflowEditor */}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <h2>Select an item to edit</h2>
              <p>Choose from the list on the left, or create a new {mode.slice(0, -1)}</p>
            </div>
          )}
        </main>

        {/* Agent Panel */}
        {agentPanelOpen && (
          <aside className="agent-panel">
            <div className="agent-header">
              <h3>Agent</h3>
              <button className="btn-close" onClick={() => setAgentPanelOpen(false)}>
                ×
              </button>
            </div>

            {/* Chat Messages */}
            <div className="chat-messages">
              {chatMessages.length === 0 ? (
                <div className="chat-empty">
                  <p>Ask me anything about your model</p>
                  <ul>
                    <li>Explain a calculation</li>
                    <li>Suggest improvements</li>
                    <li>Help with relationships</li>
                  </ul>
                </div>
              ) : (
                chatMessages.map((msg, i) => (
                  <div key={i} className={`chat-message ${msg.role}`}>
                    {msg.content}
                  </div>
                ))
              )}
            </div>

            {/* Chat Input */}
            <form className="chat-input-form" onSubmit={handleChatSubmit}>
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask anything, @ to mention, / for actions"
              />
              <button type="submit">→</button>
            </form>

            {/* Thought Process */}
            <div className="thought-process">
              <h4>Thought Process</h4>
              <div className="thought-content">
                <p className="thought-step">Ready for your question...</p>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="quick-actions">
              <h4>Quick Actions</h4>
              <button>/explain</button>
              <button>/validate</button>
              <button>/generate</button>
            </div>
          </aside>
        )}
      </div>

      {/* Footer */}
      <footer className="editor-footer">
        <div className="footer-left">
          <span className="git-status">main</span>
          <span className="save-status">All changes saved</span>
        </div>
        <div className="footer-right">
          <button className="btn-secondary">Discard Changes</button>
          <button className="btn-primary">Save & Generate</button>
        </div>
      </footer>

      <style jsx>{`
        .model-editor {
          display: flex;
          flex-direction: column;
          height: 100vh;
          background: #f8f9fa;
        }

        .editor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 16px;
          background: white;
          border-bottom: 1px solid #ddd;
        }

        .header-left {
          display: flex;
          align-items: center;
          gap: 24px;
        }

        .header-left h1 {
          font-size: 16px;
          font-weight: 600;
          margin: 0;
        }

        .mode-tabs {
          display: flex;
          gap: 4px;
        }

        .mode-tabs button {
          padding: 6px 12px;
          border: none;
          background: none;
          cursor: pointer;
          border-radius: 4px;
          font-size: 13px;
        }

        .mode-tabs button.active {
          background: #e9ecef;
          font-weight: 500;
        }

        .header-right {
          display: flex;
          gap: 8px;
        }

        .btn-icon {
          padding: 6px 10px;
          border: none;
          background: none;
          cursor: pointer;
          border-radius: 4px;
        }

        .btn-icon:hover {
          background: #e9ecef;
        }

        .editor-body {
          display: flex;
          flex: 1;
          overflow: hidden;
        }

        .navigator-panel {
          width: 250px;
          background: white;
          border-right: 1px solid #ddd;
          display: flex;
          flex-direction: column;
        }

        .navigator-header {
          display: flex;
          gap: 8px;
          padding: 8px;
          border-bottom: 1px solid #eee;
        }

        .search-input {
          flex: 1;
          padding: 6px 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 13px;
        }

        .btn-add-new {
          padding: 6px 10px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
        }

        .item-list {
          flex: 1;
          overflow-y: auto;
        }

        .item-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 12px;
          cursor: pointer;
          border-bottom: 1px solid #f0f0f0;
        }

        .item-row:hover {
          background: #f8f9fa;
        }

        .item-row.selected {
          background: #e7f3ff;
        }

        .item-name {
          font-size: 13px;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        .status-dot.pending {
          background: #ffc107;
        }

        .status-dot.in_progress {
          background: #17a2b8;
        }

        .status-dot.completed {
          background: #28a745;
        }

        .pending-summary {
          padding: 12px;
          border-top: 1px solid #ddd;
          background: #f8f9fa;
        }

        .pending-summary h4 {
          font-size: 12px;
          margin: 0 0 8px;
        }

        .pending-item {
          display: flex;
          justify-content: space-between;
          font-size: 11px;
          padding: 4px 0;
        }

        .main-canvas {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
        }

        .empty-state,
        .placeholder-editor {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: #666;
        }

        .agent-panel {
          width: 300px;
          background: white;
          border-left: 1px solid #ddd;
          display: flex;
          flex-direction: column;
        }

        .agent-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          border-bottom: 1px solid #eee;
        }

        .agent-header h3 {
          margin: 0;
          font-size: 14px;
        }

        .btn-close {
          border: none;
          background: none;
          font-size: 18px;
          cursor: pointer;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 12px;
        }

        .chat-empty {
          color: #666;
          font-size: 13px;
        }

        .chat-empty ul {
          padding-left: 20px;
          margin: 8px 0;
        }

        .chat-message {
          padding: 8px 12px;
          margin-bottom: 8px;
          border-radius: 8px;
          font-size: 13px;
        }

        .chat-message.user {
          background: #e7f3ff;
          margin-left: 20px;
        }

        .chat-message.assistant {
          background: #f0f0f0;
          margin-right: 20px;
        }

        .chat-input-form {
          display: flex;
          padding: 8px;
          border-top: 1px solid #eee;
          gap: 8px;
        }

        .chat-input-form input {
          flex: 1;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 13px;
        }

        .chat-input-form button {
          padding: 8px 12px;
          background: #0066cc;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .thought-process,
        .quick-actions {
          padding: 12px;
          border-top: 1px solid #eee;
        }

        .thought-process h4,
        .quick-actions h4 {
          font-size: 12px;
          margin: 0 0 8px;
          color: #666;
        }

        .thought-content {
          font-size: 12px;
          color: #666;
        }

        .quick-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }

        .quick-actions button {
          padding: 4px 8px;
          font-size: 11px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
        }

        .editor-footer {
          display: flex;
          justify-content: space-between;
          padding: 8px 16px;
          background: white;
          border-top: 1px solid #ddd;
        }

        .footer-left {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #666;
        }

        .git-status {
          font-family: monospace;
        }

        .footer-right {
          display: flex;
          gap: 8px;
        }

        .btn-primary {
          padding: 6px 12px;
          background: #0066cc;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
        }

        .btn-secondary {
          padding: 6px 12px;
          background: white;
          border: 1px solid #ddd;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
        }
      `}</style>
    </div>
  );
};

export default ModelEditor;
