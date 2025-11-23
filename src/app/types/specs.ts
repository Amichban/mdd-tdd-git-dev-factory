/**
 * TypeScript types for JSON specs
 * These match the JSON Schema definitions
 */

// Entity Types
export interface Entity {
  id: string;
  name: string;
  description: string;
  properties: Property[];
  relationships?: Relationship[];
  actions?: Action[];
  indexes?: Index[];
}

export interface Property {
  id: string;
  name: string;
  type: PropertyType;
  description: string;
  required?: boolean;
  constraints?: Constraints;
  values?: string[]; // For enum type
  default?: any;
  calculatedBy?: string;
  auto?: 'now' | 'uuid' | 'increment';
}

export type PropertyType =
  | 'string'
  | 'number'
  | 'integer'
  | 'boolean'
  | 'datetime'
  | 'date'
  | 'enum'
  | 'array'
  | 'object';

export interface Constraints {
  min?: number;
  max?: number;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  precision?: number;
}

export interface Relationship {
  id: string;
  name: string;
  targetEntity: string;
  type: RelationshipType;
  required?: boolean;
  description: string;
  cascade?: 'none' | 'delete' | 'nullify';
}

export type RelationshipType =
  | 'one-to-one'
  | 'one-to-many'
  | 'many-to-one'
  | 'many-to-many';

export interface Action {
  id: string;
  name: string;
  description: string;
  parameters?: ActionParameter[];
  preconditions?: string[];
  postconditions?: string[];
  workflowId?: string;
}

export interface ActionParameter {
  id: string;
  type: string;
  required?: boolean;
}

export interface Index {
  fields: string[];
  unique?: boolean;
}

// Algorithm Types
export interface Algorithm {
  id: string;
  name: string;
  description: string;
  inputs: AlgorithmInput[];
  output: AlgorithmOutput;
  steps: AlgorithmStep[];
  finalFormula?: string;
  tests?: AlgorithmTest[];
}

export interface AlgorithmInput {
  id: string;
  name: string;
  type: string;
  description: string;
  constraints?: {
    min?: number;
    max?: number;
  };
}

export interface AlgorithmOutput {
  type: string;
  min?: number;
  max?: number;
  description?: string;
}

export interface AlgorithmStep {
  id: string;
  name: string;
  description: string;
  formula: string;
  weight?: number;
}

export interface AlgorithmTest {
  inputs: Record<string, any>;
  expected: any;
  tolerance?: number;
  description?: string;
}

// Workflow Types
export interface Workflow {
  id: string;
  name: string;
  description: string;
  trigger?: WorkflowTrigger;
  states: WorkflowState[];
  transitions: WorkflowTransition[];
  sla?: Record<string, string>;
}

export interface WorkflowTrigger {
  type: 'event' | 'schedule' | 'manual' | 'condition';
  event?: string;
  schedule?: string;
  condition?: string;
}

export interface WorkflowState {
  id: string;
  name: string;
  type: 'initial' | 'intermediate' | 'final';
  description?: string;
  onEnter?: string[];
  onExit?: string[];
}

export interface WorkflowTransition {
  id: string;
  name: string;
  from: string;
  to: string;
  trigger: string;
  timerDuration?: string;
  conditions?: string[];
  actions?: string[];
}

// Spec File Types
export interface EntitiesSpec {
  $schema?: string;
  version: string;
  entities: Entity[];
}

export interface AlgorithmsSpec {
  $schema?: string;
  version: string;
  algorithms: Algorithm[];
}

export interface WorkflowsSpec {
  $schema?: string;
  version: string;
  workflows: Workflow[];
}

// UI State Types
export interface EditorState {
  selectedEntity?: string;
  selectedAlgorithm?: string;
  selectedWorkflow?: string;
  pendingChanges: PendingChange[];
  gitStatus: GitStatus;
}

export interface PendingChange {
  type: 'entity' | 'algorithm' | 'workflow';
  id: string;
  action: 'add' | 'modify' | 'delete';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  issueNumber?: number;
  prNumber?: number;
}

export interface GitStatus {
  branch: string;
  hasChanges: boolean;
  ahead: number;
  behind: number;
}
