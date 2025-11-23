/**
 * Graph Types for Business Model Visualization
 *
 * Implements stable ID patterns like:
 * - entity.customer
 * - wf.monthly_billing
 * - rule.data_freshness
 * - algo.risk_calc
 */

export type NodeType = 'entity' | 'workflow' | 'rule' | 'algorithm' | 'tool' | 'queue' | 'job';

export type NodeStatus = 'healthy' | 'degraded' | 'error' | 'unknown';

export type EdgeType = 'data_flow' | 'triggers' | 'depends_on' | 'validates';

export type Criticality = 'low' | 'medium' | 'high' | 'critical';

export type Layer = 'domain' | 'infrastructure' | 'operational';

export interface GraphNode {
  id: string; // "entity.customer", "wf.monthly_billing"
  type: NodeType;
  layer: Layer;
  label: string;
  description: string;
  explanation_template?: string;
  metadata: {
    owner?: string;
    criticality?: Criticality;
    sla?: {
      freshness?: string;
      quality?: number;
    };
    tags?: string[];
  };
  status?: NodeStatus;
  health_score?: number;
  position?: {
    x: number;
    y: number;
  };
}

export interface GraphEdge {
  id: string;
  source: string; // node.id
  target: string; // node.id
  type: EdgeType;
  label?: string;
  metadata?: {
    latency?: string;
    volume?: string;
    frequency?: string;
  };
  animated?: boolean;
}

export interface Graph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: {
    version: string;
    lastUpdated: string;
  };
}

/**
 * Event Types for Observer System
 */

export type EventType =
  | 'node_status_changed'
  | 'lineage_violation'
  | 'sla_breach'
  | 'quality_degradation'
  | 'job_started'
  | 'job_completed'
  | 'job_failed'
  | 'step_completed'
  | 'step_failed'
  // Algorithm-level decision events for explainability
  | 'decision_evaluated'
  | 'result_computed';

export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

/**
 * Decision Event - Emitted when algorithm evaluates a condition
 */
export interface DecisionEvent {
  event_type: 'decision_evaluated';
  correlation_id: string;
  node_id: string; // e.g., "algo.california_tax"
  timestamp: string;
  step: string; // Decision point ID, e.g., "check_state"
  condition: boolean; // Result of evaluation
  reason: string; // Human-readable explanation
  impact: string; // What this decision means for the outcome
}

/**
 * Result Event - Emitted when algorithm produces final result
 */
export interface ResultEvent {
  event_type: 'result_computed';
  correlation_id: string;
  node_id: string;
  timestamp: string;
  result: any; // The computed value
  summary: string; // Human-readable summary
  formula?: string; // The calculation formula used
}

export interface NodeStatusEvent {
  event_type: EventType;
  node_id: string;
  status: NodeStatus;
  severity: Severity;
  correlation_id: string; // Links to job run for full trace
  timestamp: string; // ISO 8601
  summary: string;
  details_url: string;
  affected_downstream?: string[]; // Other node IDs impacted
  suggested_actions?: string[]; // Slash commands to remediate
}

/**
 * Agent Session Types
 */

export interface AgentSession {
  id: string;
  user_id: string;
  workspace_id: string;
  role_id: string;
  business_model_snapshot: {
    entities: Record<string, any>;
    workflows: Record<string, any>;
    rules: Record<string, any>;
    algorithms: Record<string, any>;
  };
  context_files: string[]; // Paths to business_model/*.yaml
  permissions: string[];
  created_at: string;
  last_activity: string;
}

/**
 * GenUI Widget Types - Versioned Protocol
 */

export type WidgetName =
  | 'confirm-action'
  | 'data-preview'
  | 'approval-request'
  | 'timeline-view'
  | 'schema-migration'
  | 'retry-action'
  | 'impact-analysis';

export interface GenUIWidget {
  type: 'widget';
  version: '1';
  name: WidgetName;
  data: {
    title: string;
    description: string;
    cmd?: string; // Predefined slash command only
    job_id?: string;
    correlation_id?: string;
    preview_url?: string;
    requires_approval?: boolean;
    affected_nodes?: string[];
  };
}

/**
 * Job Run Types for Explainability
 */

export interface JobRunEvent {
  id: string;
  timestamp: string;
  type: 'started' | 'step_completed' | 'step_failed' | 'completed' | 'failed';
  message: string;
  metadata?: Record<string, any>;
}

export interface RuleEvaluation {
  rule_id: string;
  rule_name: string;
  passed: boolean;
  reason?: string;
  timestamp: string;
}

export interface JobRun {
  id: string; // correlation_id
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
  suggested_remediation?: GenUIWidget;
}
