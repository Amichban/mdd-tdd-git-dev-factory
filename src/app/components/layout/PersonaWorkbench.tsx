/**
 * Persona Workbench Component - Mission Control Layout
 *
 * "Command Center" Agentic UI using Bento 3-Column Layout:
 * - Zone A: Pulse (left, 20%) - Situational awareness
 * - Zone B: Active Canvas (center, 50%) - Deep work
 * - Zone C: Co-Pilot & Context (right, 30%) - Agent interaction
 *
 * Features:
 * - Progressive disclosure (Summary → Detailed → Technical)
 * - Agent reasoning stream with correlation IDs
 * - Polymorphic canvas modes
 * - Event signals with structured schema
 */

import React, { useState } from 'react';

// Progressive disclosure levels
type DisclosureLevel = 'summary' | 'detailed' | 'technical';

// Event signal with correlation for lineage
interface EventSignal {
  event_type: string;
  node_id: string;
  status: 'success' | 'warning' | 'error';
  severity: 'low' | 'medium' | 'high' | 'critical';
  correlation_id: string;
  timestamp: string;
  summary: string;
  details_url?: string;
}

interface WorkItem {
  id: string;
  title: string;
  subtitle: string;
  urgency: 'high' | 'medium' | 'low';
  strength?: number;
  slaRemaining?: string;
  correlation_id?: string;
  layer?: 'domain' | 'infrastructure' | 'operational';
}

interface DataSource {
  id: string;
  name: string;
  value: any;
  timestamp?: string;
  layer?: 'domain' | 'infrastructure' | 'operational';
}

interface CalculationStep {
  id: string;
  name: string;
  value: number;
  weight: number;
  description: string;
}

// Knowledge graph entry for context panel
interface KnowledgeEntry {
  term: string;
  definition: string;
  owner?: string;
  lastAudited?: string;
}

interface PersonaWorkbenchProps {
  personaName: string;
  personaTitle: string;
  roleId: string;
  workItems: WorkItem[];
  dataSources: DataSource[];
  calculationSteps: CalculationStep[];
  knowledgeEntries?: KnowledgeEntry[];
  eventSignals?: EventSignal[];
  onApprove: (itemId: string, reasoning: string) => void;
  onReject: (itemId: string, reasoning: string) => void;
  onAskAgent: (question: string) => void;
  onExplain?: (correlationId: string) => void;
}

// Canvas modes for polymorphic workspace
type CanvasMode = 'investigation' | 'doc_building' | 'code_view';
type CanvasTab = 'data' | 'calculations' | 'workflow' | 'documents';

// Agent reasoning step with structured output
interface ReasoningStep {
  id: string;
  action: string;
  status: 'pending' | 'running' | 'complete';
  result?: string;
}

export const PersonaWorkbench: React.FC<PersonaWorkbenchProps> = ({
  personaName,
  personaTitle,
  roleId,
  workItems,
  dataSources,
  calculationSteps,
  knowledgeEntries = [],
  eventSignals = [],
  onApprove,
  onReject,
  onAskAgent,
  onExplain,
}) => {
  const [selectedItemId, setSelectedItemId] = useState<string | null>(
    workItems[0]?.id || null
  );
  const [activeTab, setActiveTab] = useState<CanvasTab>('data');
  const [disclosureLevel, setDisclosureLevel] = useState<DisclosureLevel>('summary');
  const [canvasMode, setCanvasMode] = useState<CanvasMode>('investigation');
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [chatInput, setChatInput] = useState('');
  const [reasoningSteps, setReasoningSteps] = useState<ReasoningStep[]>([]);
  const [activeKnowledge, setActiveKnowledge] = useState<KnowledgeEntry | null>(
    knowledgeEntries[0] || null
  );

  const selectedItem = workItems.find((item) => item.id === selectedItemId);

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    setChatMessages([...chatMessages, { role: 'user', content: chatInput }]);
    onAskAgent(chatInput);

    // Structured reasoning steps
    const steps: ReasoningStep[] = [
      { id: '1', action: 'Parsing question', status: 'complete' },
      { id: '2', action: 'Loading Registry (business model)', status: 'running' },
      { id: '3', action: 'Querying Observer (recent events)', status: 'pending' },
      { id: '4', action: 'Generating explanation', status: 'pending' },
    ];
    setReasoningSteps(steps);

    // Simulate progressive completion
    setTimeout(() => {
      setReasoningSteps(prev => prev.map(s =>
        s.id === '2' ? { ...s, status: 'complete' as const, result: 'Found 3 related entities' } : s
      ).map(s =>
        s.id === '3' ? { ...s, status: 'running' as const } : s
      ));
    }, 500);

    setTimeout(() => {
      setReasoningSteps(prev => prev.map(s =>
        s.id === '3' ? { ...s, status: 'complete' as const, result: '5 events in last hour' } : s
      ).map(s =>
        s.id === '4' ? { ...s, status: 'running' as const } : s
      ));
    }, 1000);

    // Final response
    setTimeout(() => {
      setReasoningSteps(prev => prev.map(s =>
        s.id === '4' ? { ...s, status: 'complete' as const } : s
      ));
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Based on the Registry and Observer data, I can explain that...`,
        },
      ]);
    }, 1500);

    setChatInput('');
  };

  // Get severity color for event signals
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#ffc107';
      default: return '#28a745';
    }
  };

  // Get layer badge color
  const getLayerColor = (layer?: string) => {
    switch (layer) {
      case 'domain': return '#0d6efd';
      case 'infrastructure': return '#6f42c1';
      case 'operational': return '#20c997';
      default: return '#6c757d';
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'high':
        return '#dc3545';
      case 'medium':
        return '#ffc107';
      default:
        return '#28a745';
    }
  };

  return (
    <div className="persona-workbench">
      {/* Header */}
      <header className="workbench-header">
        <div className="header-left">
          <div className="persona-badge">{personaTitle}</div>
          <h1>{personaName}</h1>
        </div>
        <div className="header-right">
          <div className="quick-actions">
            <button className="btn-quick">Refresh</button>
            <button className="btn-quick">Export</button>
            <button className="btn-quick">Settings</button>
          </div>
          <div className="notifications">
            <span className="notification-badge">3</span>
            🔔
          </div>
          <div className="user-avatar">JD</div>
        </div>
      </header>

      <div className="workbench-body">
        {/* Zone A: Pulse - Situational Awareness */}
        <aside className="zone-a-pulse">
          <div className="zone-header">
            <h3>Pulse</h3>
            <div className="disclosure-toggle">
              <button
                className={disclosureLevel === 'summary' ? 'active' : ''}
                onClick={() => setDisclosureLevel('summary')}
                title="Summary view"
              >S</button>
              <button
                className={disclosureLevel === 'detailed' ? 'active' : ''}
                onClick={() => setDisclosureLevel('detailed')}
                title="Detailed view"
              >D</button>
              <button
                className={disclosureLevel === 'technical' ? 'active' : ''}
                onClick={() => setDisclosureLevel('technical')}
                title="Technical view"
              >T</button>
            </div>
          </div>

          <div className="queue-filters">
            <button className="filter-btn active">All</button>
            <button className="filter-btn">Urgent</button>
            <button className="filter-btn">Mine</button>
          </div>

          {/* Smart Priority Feed */}
          <div className="priority-feed">
            {workItems.map((item) => (
              <div
                key={item.id}
                className={`pulse-card ${selectedItemId === item.id ? 'selected' : ''}`}
                onClick={() => setSelectedItemId(item.id)}
              >
                <div className="card-header">
                  <div className="urgency-indicator" style={{ background: getUrgencyColor(item.urgency) }} />
                  {item.layer && (
                    <span className="layer-badge" style={{ background: getLayerColor(item.layer) }}>
                      {item.layer[0].toUpperCase()}
                    </span>
                  )}
                </div>

                {/* Summary Level - Always shown */}
                <div className="card-summary">
                  <div className="item-title">{item.title}</div>
                  {item.slaRemaining && (
                    <div className="sla-chip">{item.slaRemaining}</div>
                  )}
                </div>

                {/* Detailed Level */}
                {(disclosureLevel === 'detailed' || disclosureLevel === 'technical') && (
                  <div className="card-detailed">
                    <div className="item-subtitle">{item.subtitle}</div>
                    {item.strength !== undefined && (
                      <div className="strength-display">
                        <span className="strength-label">Confidence</span>
                        <div className="strength-bar">
                          <div
                            className="strength-fill"
                            style={{ width: `${item.strength * 100}%` }}
                          />
                        </div>
                        <span className="strength-value">{(item.strength * 100).toFixed(0)}%</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Technical Level */}
                {disclosureLevel === 'technical' && item.correlation_id && (
                  <div className="card-technical">
                    <code className="correlation-id">{item.correlation_id}</code>
                    <button
                      className="btn-explain"
                      onClick={(e) => {
                        e.stopPropagation();
                        onExplain?.(item.correlation_id!);
                      }}
                    >
                      Explain
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Recent Events */}
          {eventSignals.length > 0 && (
            <div className="events-section">
              <h4>Recent Events</h4>
              <div className="event-list">
                {eventSignals.slice(0, 5).map((event, i) => (
                  <div key={i} className="event-item">
                    <div
                      className="event-indicator"
                      style={{ background: getSeverityColor(event.severity) }}
                    />
                    <div className="event-content">
                      <div className="event-summary">{event.summary}</div>
                      <div className="event-meta">
                        <span className="event-time">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </span>
                        <span className="event-node">{event.node_id}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </aside>

        {/* Main Canvas */}
        <main className="main-canvas">
          {selectedItem ? (
            <>
              {/* Item Header */}
              <div className="canvas-header">
                <h2>{selectedItem.title}</h2>
                <span className="item-id">#{selectedItem.id}</span>
              </div>

              {/* Canvas Tabs */}
              <div className="canvas-tabs">
                <button
                  className={activeTab === 'data' ? 'active' : ''}
                  onClick={() => setActiveTab('data')}
                >
                  📊 Data
                </button>
                <button
                  className={activeTab === 'calculations' ? 'active' : ''}
                  onClick={() => setActiveTab('calculations')}
                >
                  🧮 Calculations
                </button>
                <button
                  className={activeTab === 'workflow' ? 'active' : ''}
                  onClick={() => setActiveTab('workflow')}
                >
                  🔄 Workflow
                </button>
                <button
                  className={activeTab === 'documents' ? 'active' : ''}
                  onClick={() => setActiveTab('documents')}
                >
                  📄 Documents
                </button>
              </div>

              {/* Tab Content */}
              <div className="canvas-content">
                {/* Data Tab */}
                {activeTab === 'data' && (
                  <div className="data-tab">
                    <div className="data-section">
                      <h4>Data Sources</h4>
                      <div className="data-grid">
                        {dataSources.map((source) => (
                          <div key={source.id} className="data-card">
                            <div className="data-label">{source.name}</div>
                            <div className="data-value">{String(source.value)}</div>
                            {source.timestamp && (
                              <div className="data-timestamp">{source.timestamp}</div>
                            )}
                          </div>
                        ))}
                      </div>
                      <div className="data-actions">
                        <button className="btn-link">View Lineage</button>
                        <button className="btn-link">Refresh Data</button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Calculations Tab */}
                {activeTab === 'calculations' && (
                  <div className="calculations-tab">
                    <div className="calc-result">
                      <h4>Signal Strength</h4>
                      <div className="result-value">
                        {selectedItem.strength !== undefined
                          ? `${(selectedItem.strength * 100).toFixed(0)}%`
                          : 'N/A'}
                      </div>
                    </div>

                    <div className="calc-breakdown">
                      <h4>Calculation Breakdown</h4>
                      {calculationSteps.map((step) => (
                        <div key={step.id} className="calc-step">
                          <div className="step-header">
                            <span className="step-name">{step.name}</span>
                            <span className="step-value">{step.value.toFixed(2)}</span>
                          </div>
                          <div className="step-weight">× {(step.weight * 100).toFixed(0)}% weight</div>
                          <div className="step-description">{step.description}</div>
                        </div>
                      ))}
                    </div>

                    <div className="calc-actions">
                      <button className="btn-secondary">What-if Analysis</button>
                      <button className="btn-secondary">Explain Formula</button>
                    </div>
                  </div>
                )}

                {/* Workflow Tab */}
                {activeTab === 'workflow' && (
                  <div className="workflow-tab">
                    <div className="workflow-diagram">
                      <div className="workflow-state completed">Pending</div>
                      <div className="workflow-arrow">→</div>
                      <div className="workflow-state current">Under Review</div>
                      <div className="workflow-arrow">→</div>
                      <div className="workflow-state">Approved</div>
                      <div className="workflow-arrow">→</div>
                      <div className="workflow-state">Executed</div>
                    </div>

                    <div className="workflow-history">
                      <h4>History</h4>
                      <div className="history-item">
                        <span className="history-time">10:30 AM</span>
                        <span>Signal generated</span>
                      </div>
                      <div className="history-item">
                        <span className="history-time">10:32 AM</span>
                        <span>Assigned for review</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Documents Tab */}
                {activeTab === 'documents' && (
                  <div className="documents-tab">
                    <div className="doc-list">
                      <div className="doc-item">
                        <span className="doc-icon">📄</span>
                        <span className="doc-name">Signal Analysis Report</span>
                        <button className="btn-link">View</button>
                      </div>
                      <div className="doc-item">
                        <span className="doc-icon">📊</span>
                        <span className="doc-name">Historical Performance</span>
                        <button className="btn-link">View</button>
                      </div>
                    </div>
                    <button className="btn-secondary">Generate Report</button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <h3>Select an item from the queue</h3>
            </div>
          )}
        </main>

        {/* Zone C: Co-Pilot & Context */}
        <aside className="zone-c-copilot">
          {/* Top Half: Agent Dialogue */}
          <div className="agent-dialogue">
            <div className="dialogue-header">
              <h3>Co-Pilot</h3>
              <span className="role-badge">{roleId}</span>
            </div>

            <div className="chat-messages">
              {chatMessages.length === 0 ? (
                <div className="chat-placeholder">
                  <p>Ask me anything about this item</p>
                  <div className="suggestions">
                    <button onClick={() => setChatInput('Explain why this was flagged')}>
                      Why flagged?
                    </button>
                    <button onClick={() => setChatInput('Draft a response to stakeholders')}>
                      Draft response
                    </button>
                    <button onClick={() => setChatInput('Compare with similar items')}>
                      Compare similar
                    </button>
                  </div>
                </div>
              ) : (
                chatMessages.map((msg, i) => (
                  <div key={i} className={`message ${msg.role}`}>
                    {msg.content}
                  </div>
                ))
              )}
            </div>

            <form className="chat-input" onSubmit={handleChatSubmit}>
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask anything, @ to mention, / for actions"
              />
              <button type="submit">Send</button>
            </form>
          </div>

          {/* Reasoning Stream */}
          <div className="reasoning-stream">
            <h4>Reasoning</h4>
            {reasoningSteps.length > 0 ? (
              <div className="reasoning-steps">
                {reasoningSteps.map((step) => (
                  <div key={step.id} className={`reasoning-step ${step.status}`}>
                    <span className="step-status">
                      {step.status === 'complete' ? '✓' : step.status === 'running' ? '◉' : '○'}
                    </span>
                    <div className="step-content">
                      <span className="step-action">{step.action}</span>
                      {step.result && (
                        <span className="step-result">{step.result}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="reasoning-idle">
                <span className="idle-icon">🧠</span>
                Ready for your question...
              </div>
            )}
          </div>

          {/* Bottom Half: Dynamic Knowledge Graph */}
          <div className="knowledge-graph">
            <h4>Context</h4>
            {activeKnowledge ? (
              <div className="knowledge-card">
                <div className="knowledge-term">{activeKnowledge.term}</div>
                <div className="knowledge-definition">{activeKnowledge.definition}</div>
                {activeKnowledge.owner && (
                  <div className="knowledge-meta">
                    <span>Owner: {activeKnowledge.owner}</span>
                  </div>
                )}
                {activeKnowledge.lastAudited && (
                  <div className="knowledge-meta">
                    <span>Last audited: {activeKnowledge.lastAudited}</span>
                  </div>
                )}
              </div>
            ) : (
              <div className="knowledge-empty">
                Select an item to see related context
              </div>
            )}
          </div>

          {/* Data Sources */}
          <div className="sources-section">
            <h4>Sources</h4>
            <div className="source-list">
              {dataSources.slice(0, 4).map((source) => (
                <div key={source.id} className="source-item">
                  {source.layer && (
                    <span className="source-layer" style={{ background: getLayerColor(source.layer) }}>
                      {source.layer[0].toUpperCase()}
                    </span>
                  )}
                  <span className="source-name">{source.name}</span>
                </div>
              ))}
            </div>
            <button className="btn-link">View Data Dictionary</button>
          </div>

          {/* Tools */}
          <div className="tools-section">
            <h4>Tools</h4>
            <div className="tool-grid">
              <button className="tool-btn">Calculate</button>
              <button className="tool-btn">Chart</button>
              <button className="tool-btn">Compare</button>
              <button className="tool-btn">Export</button>
            </div>
          </div>
        </aside>
      </div>

      {/* Footer */}
      <footer className="workbench-footer">
        <div className="footer-left">
          <button
            className="btn-primary success"
            onClick={() => onApprove(selectedItemId || '', 'Approved')}
            disabled={!selectedItemId}
          >
            ✓ Approve
          </button>
          <button
            className="btn-primary danger"
            onClick={() => onReject(selectedItemId || '', 'Rejected')}
            disabled={!selectedItemId}
          >
            ✗ Reject
          </button>
        </div>

        <div className="footer-center">
          <button className="btn-secondary">Generate Report</button>
          <button className="btn-secondary">Export CSV</button>
          <button className="btn-secondary">Share</button>
        </div>

        <div className="footer-right">
          <span className="git-status">main</span>
        </div>
      </footer>

      <style jsx>{`
        .persona-workbench {
          display: flex;
          flex-direction: column;
          height: 100vh;
          background: #0a0a0a;
          color: #e5e7eb;
          font-family: 'Inter', -apple-system, system-ui, sans-serif;
          font-weight: 400;
          -webkit-font-smoothing: antialiased;
        }

        /* Header - Antigravity floating */
        .workbench-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 20px;
          background: rgba(17, 17, 17, 0.8);
          backdrop-filter: blur(20px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }

        .header-left {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .persona-badge {
          padding: 6px 12px;
          background: rgba(59, 130, 246, 0.15);
          border: 1px solid rgba(59, 130, 246, 0.3);
          border-radius: 8px;
          font-size: 11px;
          font-weight: 500;
          color: #60a5fa;
        }

        .header-left h1 {
          margin: 0;
          font-size: 14px;
          font-weight: 500;
          color: #f3f4f6;
        }

        .header-right {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .quick-actions {
          display: flex;
          gap: 6px;
        }

        .btn-quick {
          padding: 6px 12px;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 8px;
          color: #9ca3af;
          font-size: 11px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .btn-quick:hover {
          background: rgba(255, 255, 255, 0.06);
          border-color: rgba(255, 255, 255, 0.12);
          color: #e5e7eb;
        }

        .notifications {
          position: relative;
          cursor: pointer;
          padding: 6px;
        }

        .notification-badge {
          position: absolute;
          top: 2px;
          right: 2px;
          width: 14px;
          height: 14px;
          background: #ef4444;
          border-radius: 50%;
          font-size: 9px;
          font-weight: 600;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .user-avatar {
          width: 32px;
          height: 32px;
          background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 11px;
          font-weight: 600;
          color: #fff;
        }

        /* Body */
        .workbench-body {
          display: flex;
          flex: 1;
          overflow: hidden;
          padding: 12px;
          gap: 12px;
          background: #0a0a0a;
        }

        /* Zone A: Pulse (20% width) - Floating glass panel */
        .zone-a-pulse {
          width: 20%;
          min-width: 260px;
          background: rgba(17, 17, 17, 0.6);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 16px;
          display: flex;
          flex-direction: column;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .zone-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }

        .zone-header h3 {
          margin: 0;
          font-size: 13px;
          font-weight: 600;
          color: #f3f4f6;
        }

        .disclosure-toggle {
          display: flex;
          gap: 4px;
        }

        .disclosure-toggle button {
          width: 26px;
          height: 26px;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 6px;
          color: #6b7280;
          font-size: 10px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .disclosure-toggle button:hover {
          background: rgba(255, 255, 255, 0.06);
        }

        .disclosure-toggle button.active {
          background: rgba(59, 130, 246, 0.2);
          border-color: rgba(59, 130, 246, 0.4);
          color: #60a5fa;
        }

        .queue-filters {
          display: flex;
          gap: 6px;
          padding: 12px 16px;
        }

        .filter-btn {
          padding: 6px 12px;
          background: transparent;
          border: none;
          color: #6b7280;
          font-size: 11px;
          font-weight: 500;
          cursor: pointer;
          border-radius: 8px;
          transition: all 0.2s ease;
        }

        .filter-btn:hover {
          color: #9ca3af;
        }

        .filter-btn.active {
          background: rgba(255, 255, 255, 0.06);
          color: #e5e7eb;
        }

        .priority-feed {
          flex: 1;
          overflow-y: auto;
          padding: 8px 12px;
        }

        .pulse-card {
          background: rgba(255, 255, 255, 0.02);
          border-radius: 12px;
          padding: 12px;
          margin-bottom: 8px;
          cursor: pointer;
          border: 1px solid rgba(255, 255, 255, 0.04);
          transition: all 0.2s ease;
        }

        .pulse-card:hover {
          background: rgba(255, 255, 255, 0.04);
          border-color: rgba(255, 255, 255, 0.08);
        }

        .pulse-card.selected {
          background: rgba(59, 130, 246, 0.08);
          border-color: rgba(59, 130, 246, 0.3);
        }

        .card-header {
          display: flex;
          align-items: center;
          gap: 6px;
          margin-bottom: 6px;
        }

        .urgency-indicator {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        .layer-badge {
          padding: 2px 4px;
          border-radius: 3px;
          font-size: 9px;
          font-weight: 600;
          color: #fff;
        }

        .card-summary {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }

        .item-title {
          font-size: 12px;
          font-weight: 500;
          flex: 1;
        }

        .sla-chip {
          font-size: 9px;
          padding: 2px 6px;
          background: #ffc10733;
          color: #ffc107;
          border-radius: 10px;
        }

        .card-detailed {
          margin-top: 8px;
          padding-top: 8px;
          border-top: 1px solid #3d3d3d;
        }

        .item-subtitle {
          font-size: 11px;
          color: #999;
        }

        .strength-display {
          display: flex;
          align-items: center;
          gap: 6px;
          margin-top: 6px;
        }

        .strength-label {
          font-size: 10px;
          color: #666;
        }

        .strength-bar {
          flex: 1;
          height: 4px;
          background: #3d3d3d;
          border-radius: 2px;
          overflow: hidden;
        }

        .strength-fill {
          height: 100%;
          background: #4da6ff;
        }

        .strength-value {
          font-size: 10px;
          color: #4da6ff;
          font-family: monospace;
        }

        .card-technical {
          margin-top: 8px;
          padding-top: 8px;
          border-top: 1px solid #3d3d3d;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .correlation-id {
          font-size: 9px;
          color: #666;
          background: #1a1a1a;
          padding: 2px 4px;
          border-radius: 3px;
        }

        .btn-explain {
          font-size: 10px;
          padding: 3px 8px;
          background: #6f42c1;
          border: none;
          border-radius: 3px;
          color: #fff;
          cursor: pointer;
        }

        .events-section {
          padding: 12px;
          border-top: 1px solid #3d3d3d;
        }

        .events-section h4 {
          margin: 0 0 8px;
          font-size: 11px;
          color: #999;
          text-transform: uppercase;
        }

        .event-list {
          max-height: 150px;
          overflow-y: auto;
        }

        .event-item {
          display: flex;
          gap: 8px;
          padding: 6px 0;
          border-bottom: 1px solid #3d3d3d;
        }

        .event-indicator {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          margin-top: 4px;
        }

        .event-content {
          flex: 1;
        }

        .event-summary {
          font-size: 11px;
        }

        .event-meta {
          display: flex;
          gap: 8px;
          font-size: 9px;
          color: #666;
          margin-top: 2px;
        }

        /* Main Canvas - Zone B (50% width) - Floating glass panel */
        .main-canvas {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          background: rgba(17, 17, 17, 0.6);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 16px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .canvas-header {
          display: flex;
          align-items: baseline;
          gap: 12px;
          padding: 20px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }

        .canvas-header h2 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: #f3f4f6;
        }

        .item-id {
          font-size: 11px;
          color: #6b7280;
          font-family: 'JetBrains Mono', monospace;
          padding: 4px 8px;
          background: rgba(255, 255, 255, 0.03);
          border-radius: 6px;
        }

        .canvas-tabs {
          display: flex;
          padding: 0 20px;
          gap: 4px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }

        .canvas-tabs button {
          padding: 14px 16px;
          background: transparent;
          border: none;
          color: #6b7280;
          font-size: 12px;
          font-weight: 500;
          cursor: pointer;
          border-bottom: 2px solid transparent;
          transition: all 0.2s ease;
        }

        .canvas-tabs button:hover {
          color: #9ca3af;
        }

        .canvas-tabs button.active {
          color: #f3f4f6;
          border-bottom-color: #3b82f6;
        }

        .canvas-content {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
        }

        /* Data Tab */
        .data-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
          gap: 12px;
          margin-bottom: 20px;
        }

        .data-card {
          padding: 16px;
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.04);
          border-radius: 12px;
          transition: all 0.2s ease;
        }

        .data-card:hover {
          background: rgba(255, 255, 255, 0.04);
        }

        .data-label {
          font-size: 11px;
          color: #6b7280;
          margin-bottom: 6px;
          font-weight: 500;
        }

        .data-value {
          font-size: 18px;
          font-weight: 600;
          font-family: 'JetBrains Mono', monospace;
          color: #f3f4f6;
        }

        .data-timestamp {
          font-size: 10px;
          color: #4b5563;
          margin-top: 6px;
        }

        /* Calculations Tab */
        .calc-result {
          text-align: center;
          padding: 24px;
          background: #2d2d2d;
          border-radius: 8px;
          margin-bottom: 16px;
        }

        .calc-result h4 {
          margin: 0 0 8px;
          font-size: 12px;
          color: #999;
        }

        .result-value {
          font-size: 48px;
          font-weight: 600;
          color: #4da6ff;
        }

        .calc-step {
          padding: 12px;
          background: #2d2d2d;
          border-radius: 6px;
          margin-bottom: 8px;
        }

        .step-header {
          display: flex;
          justify-content: space-between;
        }

        .step-name {
          font-weight: 500;
        }

        .step-value {
          font-family: monospace;
        }

        .step-weight {
          font-size: 11px;
          color: #999;
        }

        .step-description {
          font-size: 12px;
          color: #999;
          margin-top: 4px;
        }

        /* Zone C: Co-Pilot (30% width) - Floating glass panel */
        .zone-c-copilot {
          width: 30%;
          min-width: 320px;
          background: rgba(17, 17, 17, 0.6);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 16px;
          display: flex;
          flex-direction: column;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .agent-dialogue {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-height: 0;
        }

        .dialogue-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }

        .dialogue-header h3 {
          margin: 0;
          font-size: 13px;
          font-weight: 600;
          color: #f3f4f6;
        }

        .role-badge {
          font-size: 10px;
          padding: 4px 10px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          color: #9ca3af;
          font-weight: 500;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 12px;
        }

        .chat-placeholder {
          color: #999;
          font-size: 13px;
        }

        .suggestions {
          margin-top: 12px;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .suggestions button {
          padding: 8px;
          background: #3d3d3d;
          border: none;
          border-radius: 4px;
          color: #999;
          font-size: 12px;
          text-align: left;
          cursor: pointer;
        }

        .message {
          padding: 8px 12px;
          border-radius: 8px;
          margin-bottom: 8px;
          font-size: 13px;
        }

        .message.user {
          background: #0066cc;
          margin-left: 24px;
        }

        .message.assistant {
          background: #3d3d3d;
          margin-right: 24px;
        }

        .chat-input {
          display: flex;
          padding: 12px;
          gap: 8px;
          border-top: 1px solid #3d3d3d;
        }

        .chat-input input {
          flex: 1;
          padding: 8px 12px;
          background: #1a1a1a;
          border: 1px solid #3d3d3d;
          border-radius: 4px;
          color: #fff;
          font-size: 12px;
        }

        .chat-input button {
          padding: 8px 12px;
          background: #0066cc;
          border: none;
          border-radius: 4px;
          color: white;
          cursor: pointer;
        }

        .reasoning-stream,
        .knowledge-graph,
        .sources-section,
        .tools-section {
          padding: 12px;
          border-top: 1px solid #3d3d3d;
        }

        .reasoning-stream h4,
        .knowledge-graph h4,
        .sources-section h4,
        .tools-section h4 {
          margin: 0 0 8px;
          font-size: 11px;
          color: #999;
          text-transform: uppercase;
        }

        .reasoning-steps {
          font-size: 12px;
        }

        .reasoning-step {
          display: flex;
          gap: 8px;
          padding: 4px 0;
        }

        .reasoning-step.pending {
          color: #666;
        }

        .reasoning-step.running {
          color: #4da6ff;
        }

        .reasoning-step.complete {
          color: #28a745;
        }

        .step-status {
          font-size: 10px;
        }

        .step-content {
          flex: 1;
        }

        .step-action {
          display: block;
        }

        .step-result {
          display: block;
          font-size: 10px;
          color: #666;
          margin-top: 2px;
        }

        .reasoning-idle {
          font-size: 12px;
          color: #666;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .idle-icon {
          font-size: 14px;
        }

        .knowledge-card {
          background: #1a1a1a;
          border-radius: 6px;
          padding: 10px;
        }

        .knowledge-term {
          font-weight: 600;
          font-size: 13px;
          margin-bottom: 6px;
        }

        .knowledge-definition {
          font-size: 12px;
          color: #ccc;
          line-height: 1.4;
        }

        .knowledge-meta {
          font-size: 10px;
          color: #666;
          margin-top: 6px;
        }

        .knowledge-empty {
          font-size: 12px;
          color: #666;
        }

        .source-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          padding: 4px 0;
        }

        .source-layer {
          width: 16px;
          height: 16px;
          border-radius: 3px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 9px;
          font-weight: 600;
          color: #fff;
        }

        .source-name {
          font-family: monospace;
        }

        .tool-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
        }

        .tool-btn {
          padding: 8px;
          background: #3d3d3d;
          border: none;
          border-radius: 4px;
          color: #999;
          font-size: 11px;
          cursor: pointer;
        }

        .tool-btn:hover {
          background: #4d4d4d;
          color: #fff;
        }

        /* Footer - Floating glass */
        .workbench-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 20px;
          margin: 0 12px 12px;
          background: rgba(17, 17, 17, 0.8);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 12px;
        }

        .footer-left,
        .footer-center {
          display: flex;
          gap: 8px;
        }

        .btn-primary {
          padding: 10px 20px;
          border: none;
          border-radius: 10px;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .btn-primary.success {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
          box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }

        .btn-primary.success:hover {
          box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
          transform: translateY(-1px);
        }

        .btn-primary.danger {
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
          color: white;
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        }

        .btn-primary.danger:hover {
          box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
          transform: translateY(-1px);
        }

        .btn-primary:disabled {
          opacity: 0.4;
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }

        .btn-secondary {
          padding: 8px 16px;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 8px;
          color: #9ca3af;
          font-size: 11px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .btn-secondary:hover {
          background: rgba(255, 255, 255, 0.06);
          border-color: rgba(255, 255, 255, 0.12);
          color: #e5e7eb;
        }

        .btn-link {
          background: none;
          border: none;
          color: #60a5fa;
          font-size: 11px;
          font-weight: 500;
          cursor: pointer;
          padding: 0;
          transition: color 0.2s ease;
        }

        .btn-link:hover {
          color: #93c5fd;
        }

        .git-status {
          font-family: 'JetBrains Mono', monospace;
          font-size: 10px;
          color: #4b5563;
          padding: 4px 8px;
          background: rgba(255, 255, 255, 0.03);
          border-radius: 6px;
        }

        .empty-state {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: #666;
        }

        h4 {
          margin: 0 0 12px;
          font-size: 12px;
          font-weight: 500;
        }

        .data-actions,
        .calc-actions {
          margin-top: 16px;
          display: flex;
          gap: 8px;
        }

        .workflow-diagram {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 24px;
        }

        .workflow-state {
          padding: 8px 16px;
          background: #3d3d3d;
          border-radius: 4px;
          font-size: 12px;
        }

        .workflow-state.completed {
          background: #28a74533;
          color: #28a745;
        }

        .workflow-state.current {
          background: #0066cc;
          color: white;
        }

        .workflow-arrow {
          color: #666;
        }

        .history-item {
          display: flex;
          gap: 12px;
          font-size: 12px;
          padding: 8px 0;
          border-bottom: 1px solid #3d3d3d;
        }

        .history-time {
          color: #666;
        }

        .doc-list {
          margin-bottom: 16px;
        }

        .doc-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 0;
          border-bottom: 1px solid #3d3d3d;
        }

        .doc-name {
          flex: 1;
          font-size: 13px;
        }
      `}</style>
    </div>
  );
};

export default PersonaWorkbench;
