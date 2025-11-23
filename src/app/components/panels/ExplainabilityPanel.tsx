/**
 * Explainability Panel Component
 *
 * Shows full execution trace and agent explanation when user
 * clicks on a correlation ID or asks "Why did this fail?"
 *
 * Features:
 * - Timeline of events
 * - Business context (entity → workflow → rules)
 * - Agent narrative explanation
 * - GenUI remediation widget
 */

import React, { useState, useEffect } from 'react';

interface JobRunEvent {
  id: string;
  timestamp: string;
  type: 'started' | 'step_completed' | 'step_failed' | 'completed' | 'failed' | 'decision_evaluated' | 'result_computed';
  message: string;
  metadata?: Record<string, any>;
  // For decision events
  step?: string;
  condition?: boolean;
  reason?: string;
  impact?: string;
  // For result events
  result?: any;
  summary?: string;
  formula?: string;
}

interface RuleEvaluation {
  rule_id: string;
  rule_name: string;
  passed: boolean;
  reason?: string;
  timestamp: string;
}

interface JobRun {
  id: string;
  job_id: string;
  node_id: string;
  status: 'running' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  events: JobRunEvent[];
  rules_evaluated: RuleEvaluation[];
  affected_downstream: string[];
  error?: {
    message: string;
    stack?: string;
  };
  agent_explanation?: string;
}

interface BusinessContext {
  entity?: {
    id: string;
    name: string;
    description: string;
    owner?: string;
  };
  workflow?: {
    id: string;
    name: string;
    description: string;
  };
  rules: Array<{
    id: string;
    name: string;
    description: string;
  }>;
}

interface ExplainabilityPanelProps {
  correlationId: string;
  onClose: () => void;
  onAction?: (cmd: string) => void;
}

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({
  correlationId,
  onClose,
  onAction,
}) => {
  const [jobRun, setJobRun] = useState<JobRun | null>(null);
  const [context, setContext] = useState<BusinessContext | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'timeline' | 'context' | 'explanation'>('timeline');

  useEffect(() => {
    // Simulate fetching job run data
    setLoading(true);

    // In production: fetch(`/api/job-runs/${correlationId}`)
    setTimeout(() => {
      setJobRun({
        id: correlationId,
        job_id: 'job_market_data_ingest',
        node_id: 'wf.market_data_ingestion',
        status: 'failed',
        started_at: new Date(Date.now() - 300000).toISOString(),
        completed_at: new Date(Date.now() - 120000).toISOString(),
        duration_ms: 180000,
        events: [
          {
            id: 'evt_1',
            timestamp: new Date(Date.now() - 300000).toISOString(),
            type: 'started',
            message: 'Algorithm started',
          },
          {
            id: 'evt_2',
            timestamp: new Date(Date.now() - 280000).toISOString(),
            type: 'decision_evaluated',
            message: 'Check user state',
            step: 'check_state',
            condition: true,
            reason: "User state is 'CA'",
            impact: 'California tax rules apply',
          },
          {
            id: 'evt_3',
            timestamp: new Date(Date.now() - 260000).toISOString(),
            type: 'decision_evaluated',
            message: 'Check purchase amount',
            step: 'check_amount',
            condition: true,
            reason: 'Purchase amount $150.00 > $100 threshold',
            impact: 'Amount subject to tax',
          },
          {
            id: 'evt_4',
            timestamp: new Date(Date.now() - 240000).toISOString(),
            type: 'decision_evaluated',
            message: 'Check tax waiver',
            step: 'check_waiver',
            condition: false,
            reason: 'Tax waiver status: false',
            impact: 'No exemption, standard tax applies',
          },
          {
            id: 'evt_5',
            timestamp: new Date(Date.now() - 220000).toISOString(),
            type: 'result_computed',
            message: 'Tax calculated',
            result: 12.38,
            summary: 'Applied 8.25% California sales tax on $150.00',
            formula: '$150.00 × 8.25% = $12.38',
          },
          {
            id: 'evt_6',
            timestamp: new Date(Date.now() - 200000).toISOString(),
            type: 'completed',
            message: 'Algorithm completed',
            metadata: { duration_ms: 100 },
          },
        ],
        rules_evaluated: [
          {
            rule_id: 'rule.data_freshness',
            rule_name: 'Data Freshness SLA',
            passed: false,
            reason: 'Data arrived 3 minutes after SLA threshold',
            timestamp: new Date(Date.now() - 120000).toISOString(),
          },
          {
            rule_id: 'rule.vendor_fallback',
            rule_name: 'Vendor Fallback Policy',
            passed: true,
            timestamp: new Date(Date.now() - 180000).toISOString(),
          },
        ],
        affected_downstream: ['wf.risk_calc', 'wf.pnl_report', 'algo.vol_surface'],
        error: {
          message: 'SLA breach: data_freshness exceeded 5 minute threshold',
        },
        agent_explanation: `The workflow **wf.market_data_ingestion** failed due to an SLA breach.

**Root Cause:**
1. Primary vendor (Bloomberg) returned a 503 timeout at 08:15:23
2. Fallback to Refinitiv succeeded but added 2.5 minutes latency
3. Total ingestion time: 3 minutes, exceeding the 5-minute freshness SLA

**Impact:**
- **wf.risk_calc** was blocked waiting for fresh market data
- **wf.pnl_report** will use stale T-1 data
- **algo.vol_surface** may produce inaccurate surfaces

**Recommendation:**
Consider extending the timeout for Bloomberg API calls or running the fallback in parallel to reduce total latency.`,
      });

      setContext({
        entity: {
          id: 'entity.market_data',
          name: 'Market Data',
          description: 'Real-time and historical market prices',
          owner: 'Data Engineering',
        },
        workflow: {
          id: 'wf.market_data_ingestion',
          name: 'Market Data Ingestion',
          description: 'Fetches market data from vendors and stores in TimescaleDB',
        },
        rules: [
          {
            id: 'rule.data_freshness',
            name: 'Data Freshness SLA',
            description: 'Market data must be ingested within 5 minutes of market open',
          },
          {
            id: 'rule.vendor_fallback',
            name: 'Vendor Fallback Policy',
            description: 'If primary vendor fails, automatically switch to secondary',
          },
        ],
      });

      setLoading(false);
    }, 500);
  }, [correlationId]);

  const getEventIcon = (type: string, condition?: boolean) => {
    switch (type) {
      case 'started': return '▶';
      case 'step_completed': return '✓';
      case 'step_failed': return '✗';
      case 'completed': return '✓';
      case 'failed': return '✗';
      case 'decision_evaluated': return condition ? '✓' : '✗';
      case 'result_computed': return '=';
      default: return '•';
    }
  };

  const getEventColor = (type: string, condition?: boolean) => {
    switch (type) {
      case 'started': return 'var(--color-info)';
      case 'step_completed': return 'var(--color-success)';
      case 'step_failed': return 'var(--color-warning)';
      case 'completed': return 'var(--color-success)';
      case 'failed': return 'var(--color-error)';
      case 'decision_evaluated': return condition ? 'var(--color-success)' : 'var(--color-warning)';
      case 'result_computed': return 'var(--color-info)';
      default: return 'var(--color-muted)';
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="explainability-panel loading">
        <div className="panel-header">
          <h3>Loading trace...</h3>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>
        <div className="loading-skeleton">
          <div className="skeleton-line" />
          <div className="skeleton-line short" />
          <div className="skeleton-line" />
        </div>
        <style jsx>{styles}</style>
      </div>
    );
  }

  if (!jobRun) {
    return (
      <div className="explainability-panel error">
        <div className="panel-header">
          <h3>Trace not found</h3>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>
        <p>Could not find job run with ID: {correlationId}</p>
        <style jsx>{styles}</style>
      </div>
    );
  }

  return (
    <div className="explainability-panel">
      <div className="panel-header">
        <div className="header-info">
          <h3>Execution Trace</h3>
          <code className="correlation-id">{correlationId}</code>
        </div>
        <button className="btn-close" onClick={onClose}>×</button>
      </div>

      {/* Status Summary */}
      <div className={`status-summary ${jobRun.status}`}>
        <div className="status-icon">
          {jobRun.status === 'failed' ? '✗' : jobRun.status === 'completed' ? '✓' : '◉'}
        </div>
        <div className="status-info">
          <div className="status-label">{jobRun.status.toUpperCase()}</div>
          <div className="status-node">{jobRun.node_id}</div>
        </div>
        {jobRun.duration_ms && (
          <div className="status-duration">
            {(jobRun.duration_ms / 1000).toFixed(1)}s
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="panel-tabs">
        <button
          className={activeTab === 'timeline' ? 'active' : ''}
          onClick={() => setActiveTab('timeline')}
        >
          Timeline
        </button>
        <button
          className={activeTab === 'context' ? 'active' : ''}
          onClick={() => setActiveTab('context')}
        >
          Context
        </button>
        <button
          className={activeTab === 'explanation' ? 'active' : ''}
          onClick={() => setActiveTab('explanation')}
        >
          Explanation
        </button>
      </div>

      {/* Tab Content */}
      <div className="panel-content">
        {/* Timeline Tab */}
        {activeTab === 'timeline' && (
          <div className="timeline-tab">
            <div className="timeline">
              {jobRun.events.map((event, index) => (
                <div key={event.id} className={`timeline-event ${event.type}`}>
                  <div className="event-line">
                    {index < jobRun.events.length - 1 && <div className="line" />}
                  </div>
                  <div
                    className="event-icon"
                    style={{ color: getEventColor(event.type, event.condition) }}
                  >
                    {getEventIcon(event.type, event.condition)}
                  </div>
                  <div className="event-content">
                    <div className="event-message">{event.message}</div>
                    <div className="event-time">{formatTime(event.timestamp)}</div>

                    {/* Decision event details */}
                    {event.type === 'decision_evaluated' && (
                      <div className="decision-details">
                        <div className="decision-reason">{event.reason}</div>
                        <div className="decision-impact">→ {event.impact}</div>
                      </div>
                    )}

                    {/* Result event details */}
                    {event.type === 'result_computed' && (
                      <div className="result-details">
                        <div className="result-summary">{event.summary}</div>
                        {event.formula && (
                          <div className="result-formula">{event.formula}</div>
                        )}
                      </div>
                    )}

                    {/* Standard metadata */}
                    {event.metadata && (
                      <div className="event-metadata">
                        {Object.entries(event.metadata).map(([key, value]) => (
                          <span key={key} className="metadata-item">
                            {key}: {String(value)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Rules Evaluated */}
            <div className="rules-section">
              <h4>Rules Evaluated</h4>
              {jobRun.rules_evaluated.map((rule) => (
                <div key={rule.rule_id} className={`rule-item ${rule.passed ? 'passed' : 'failed'}`}>
                  <span className="rule-icon">{rule.passed ? '✓' : '✗'}</span>
                  <div className="rule-content">
                    <div className="rule-name">{rule.rule_name}</div>
                    {rule.reason && <div className="rule-reason">{rule.reason}</div>}
                  </div>
                </div>
              ))}
            </div>

            {/* Affected Downstream */}
            {jobRun.affected_downstream.length > 0 && (
              <div className="downstream-section">
                <h4>Affected Downstream</h4>
                <div className="downstream-nodes">
                  {jobRun.affected_downstream.map((nodeId) => (
                    <span key={nodeId} className="downstream-node">{nodeId}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Context Tab */}
        {activeTab === 'context' && context && (
          <div className="context-tab">
            {context.entity && (
              <div className="context-card">
                <div className="context-type">Entity</div>
                <div className="context-name">{context.entity.name}</div>
                <div className="context-id">{context.entity.id}</div>
                <div className="context-description">{context.entity.description}</div>
                {context.entity.owner && (
                  <div className="context-owner">Owner: {context.entity.owner}</div>
                )}
              </div>
            )}

            {context.workflow && (
              <div className="context-card">
                <div className="context-type">Workflow</div>
                <div className="context-name">{context.workflow.name}</div>
                <div className="context-id">{context.workflow.id}</div>
                <div className="context-description">{context.workflow.description}</div>
              </div>
            )}

            {context.rules.length > 0 && (
              <div className="context-card">
                <div className="context-type">Rules Applied</div>
                {context.rules.map((rule) => (
                  <div key={rule.id} className="context-rule">
                    <div className="rule-name">{rule.name}</div>
                    <div className="rule-description">{rule.description}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Explanation Tab */}
        {activeTab === 'explanation' && (
          <div className="explanation-tab">
            {jobRun.agent_explanation ? (
              <div className="agent-narrative">
                {jobRun.agent_explanation.split('\n').map((line, i) => {
                  if (line.startsWith('**') && line.endsWith('**')) {
                    return <h4 key={i}>{line.replace(/\*\*/g, '')}</h4>;
                  }
                  if (line.startsWith('- **')) {
                    return (
                      <div key={i} className="narrative-item">
                        {line.replace(/\*\*/g, '').replace('- ', '')}
                      </div>
                    );
                  }
                  if (line.match(/^\d+\./)) {
                    return <div key={i} className="narrative-step">{line}</div>;
                  }
                  return line ? <p key={i}>{line}</p> : <br key={i} />;
                })}
              </div>
            ) : (
              <div className="no-explanation">
                <p>Generating explanation...</p>
                <button
                  className="btn-generate"
                  onClick={() => onAction?.('/explain ' + correlationId)}
                >
                  Ask Agent to Explain
                </button>
              </div>
            )}

            {/* Remediation Actions */}
            <div className="remediation-section">
              <h4>Suggested Actions</h4>
              <div className="action-buttons">
                <button
                  className="btn-action"
                  onClick={() => onAction?.('/retry-ingestion --timeout 60s')}
                >
                  Retry with Extended Timeout
                </button>
                <button
                  className="btn-action secondary"
                  onClick={() => onAction?.('/notify-stakeholders')}
                >
                  Notify Stakeholders
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{styles}</style>
    </div>
  );
};

const styles = `
  .explainability-panel {
    background: rgba(26, 26, 26, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    max-height: 80vh;
    width: 480px;
    font-family: 'Inter', system-ui, sans-serif;
    color: #e0e0e0;

    --color-success: #34d399;
    --color-error: #f87171;
    --color-warning: #fbbf24;
    --color-info: #60a5fa;
    --color-muted: #6b7280;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .header-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .panel-header h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
  }

  .correlation-id {
    font-size: 11px;
    padding: 3px 8px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    color: #9ca3af;
  }

  .btn-close {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.05);
    border: none;
    color: #9ca3af;
    font-size: 18px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .btn-close:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
  }

  .status-summary {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    margin: 12px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.03);
  }

  .status-summary.failed {
    background: rgba(248, 113, 113, 0.1);
  }

  .status-summary.completed {
    background: rgba(52, 211, 153, 0.1);
  }

  .status-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
  }

  .status-summary.failed .status-icon {
    background: rgba(248, 113, 113, 0.2);
    color: var(--color-error);
  }

  .status-summary.completed .status-icon {
    background: rgba(52, 211, 153, 0.2);
    color: var(--color-success);
  }

  .status-info {
    flex: 1;
  }

  .status-label {
    font-size: 12px;
    font-weight: 600;
  }

  .status-node {
    font-size: 11px;
    color: #9ca3af;
    font-family: monospace;
  }

  .status-duration {
    font-size: 12px;
    color: #9ca3af;
    font-family: monospace;
  }

  .panel-tabs {
    display: flex;
    gap: 4px;
    padding: 0 12px;
  }

  .panel-tabs button {
    flex: 1;
    padding: 10px;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: #9ca3af;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .panel-tabs button.active {
    color: #fff;
    border-bottom-color: #60a5fa;
  }

  .panel-tabs button:hover:not(.active) {
    color: #d1d5db;
  }

  .panel-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px 20px;
  }

  /* Timeline */
  .timeline {
    position: relative;
  }

  .timeline-event {
    display: flex;
    gap: 12px;
    padding-bottom: 16px;
    position: relative;
  }

  .event-line {
    position: absolute;
    left: 7px;
    top: 20px;
    bottom: 0;
    width: 2px;
  }

  .event-line .line {
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.1);
  }

  .event-icon {
    width: 16px;
    height: 16px;
    font-size: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .event-content {
    flex: 1;
  }

  .event-message {
    font-size: 12px;
    font-weight: 500;
  }

  .event-time {
    font-size: 10px;
    color: #6b7280;
    margin-top: 2px;
  }

  .event-metadata {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 6px;
  }

  .metadata-item {
    font-size: 10px;
    padding: 2px 6px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
    color: #9ca3af;
    font-family: monospace;
  }

  /* Decision event styles */
  .decision-details {
    margin-top: 6px;
    padding: 8px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 6px;
    border-left: 2px solid rgba(96, 165, 250, 0.3);
  }

  .decision-reason {
    font-size: 11px;
    color: #d1d5db;
  }

  .decision-impact {
    font-size: 10px;
    color: #9ca3af;
    margin-top: 4px;
    font-style: italic;
  }

  /* Result event styles */
  .result-details {
    margin-top: 6px;
    padding: 8px;
    background: rgba(96, 165, 250, 0.1);
    border-radius: 6px;
  }

  .result-summary {
    font-size: 11px;
    color: #d1d5db;
    font-weight: 500;
  }

  .result-formula {
    font-size: 11px;
    color: #60a5fa;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 4px;
  }

  /* Timeline event type styling */
  .timeline-event.decision_evaluated .event-message {
    font-weight: 500;
  }

  .timeline-event.result_computed .event-message {
    font-weight: 600;
    color: #60a5fa;
  }

  /* Rules Section */
  .rules-section,
  .downstream-section {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .rules-section h4,
  .downstream-section h4,
  .remediation-section h4 {
    margin: 0 0 12px;
    font-size: 11px;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .rule-item {
    display: flex;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 8px;
    margin-bottom: 8px;
  }

  .rule-item.passed {
    background: rgba(52, 211, 153, 0.1);
  }

  .rule-item.failed {
    background: rgba(248, 113, 113, 0.1);
  }

  .rule-icon {
    font-size: 10px;
  }

  .rule-item.passed .rule-icon {
    color: var(--color-success);
  }

  .rule-item.failed .rule-icon {
    color: var(--color-error);
  }

  .rule-name {
    font-size: 12px;
    font-weight: 500;
  }

  .rule-reason {
    font-size: 11px;
    color: #9ca3af;
    margin-top: 2px;
  }

  .downstream-nodes {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .downstream-node {
    font-size: 11px;
    padding: 4px 8px;
    background: rgba(251, 191, 36, 0.1);
    border-radius: 6px;
    color: var(--color-warning);
    font-family: monospace;
  }

  /* Context Tab */
  .context-card {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
  }

  .context-type {
    font-size: 10px;
    font-weight: 600;
    color: #60a5fa;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
  }

  .context-name {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
  }

  .context-id {
    font-size: 11px;
    color: #6b7280;
    font-family: monospace;
    margin-bottom: 8px;
  }

  .context-description {
    font-size: 12px;
    color: #d1d5db;
    line-height: 1.5;
  }

  .context-owner {
    font-size: 11px;
    color: #9ca3af;
    margin-top: 8px;
  }

  .context-rule {
    padding: 8px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  .context-rule:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  .context-rule .rule-name {
    font-size: 12px;
    font-weight: 500;
  }

  .context-rule .rule-description {
    font-size: 11px;
    color: #9ca3af;
    margin-top: 4px;
  }

  /* Explanation Tab */
  .agent-narrative {
    font-size: 13px;
    line-height: 1.6;
  }

  .agent-narrative h4 {
    font-size: 12px;
    font-weight: 600;
    margin: 16px 0 8px;
    color: #fff;
  }

  .agent-narrative h4:first-child {
    margin-top: 0;
  }

  .agent-narrative p {
    margin: 0 0 12px;
    color: #d1d5db;
  }

  .narrative-item {
    padding: 4px 0 4px 12px;
    border-left: 2px solid rgba(96, 165, 250, 0.3);
    color: #d1d5db;
    font-size: 12px;
  }

  .narrative-step {
    padding: 4px 0;
    color: #d1d5db;
    font-size: 12px;
  }

  .remediation-section {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .action-buttons {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .btn-action {
    padding: 12px 16px;
    border-radius: 8px;
    border: none;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-action:not(.secondary) {
    background: #3b82f6;
    color: #fff;
  }

  .btn-action:not(.secondary):hover {
    background: #2563eb;
  }

  .btn-action.secondary {
    background: rgba(255, 255, 255, 0.05);
    color: #d1d5db;
  }

  .btn-action.secondary:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .no-explanation {
    text-align: center;
    padding: 24px;
    color: #9ca3af;
  }

  .btn-generate {
    margin-top: 12px;
    padding: 10px 16px;
    background: rgba(96, 165, 250, 0.1);
    border: 1px solid rgba(96, 165, 250, 0.3);
    border-radius: 8px;
    color: #60a5fa;
    font-size: 12px;
    cursor: pointer;
  }

  .btn-generate:hover {
    background: rgba(96, 165, 250, 0.2);
  }

  /* Loading State */
  .loading-skeleton {
    padding: 20px;
  }

  .skeleton-line {
    height: 12px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    margin-bottom: 12px;
    animation: pulse 1.5s infinite;
  }

  .skeleton-line.short {
    width: 60%;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

export default ExplainabilityPanel;
