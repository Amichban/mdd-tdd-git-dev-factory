#!/usr/bin/env python3
"""
Generate TypeScript types from specs.

This generator reads entity definitions and produces:
- TypeScript interfaces for all entities
- Enum types for string literals
- API response types
"""

import json
from pathlib import Path
from datetime import datetime

# Type mapping from JSON spec to TypeScript
TYPE_MAP = {
    "string": "string",
    "number": "number",
    "integer": "number",
    "boolean": "boolean",
    "datetime": "string",  # ISO date string
    "date": "string",
    "uuid": "string",
    "json": "Record<string, unknown>",
    "array": "Array",
    "object": "Record<string, unknown>",
}


def load_specs(specs_path: Path) -> dict:
    """Load all spec files."""
    specs = {}

    for filename in ["entities.json", "workflows.json", "algorithms.json"]:
        filepath = specs_path / filename
        if filepath.exists():
            with open(filepath) as f:
                key = filename.replace(".json", "")
                specs[key] = json.load(f)

    return specs


def snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def generate_enum_type(name: str, values: list[str]) -> str:
    """Generate TypeScript union type for enum values."""
    quoted = [f'"{v}"' for v in values]
    return f"export type {name} = {' | '.join(quoted)};\n"


def generate_field_type(field: dict) -> str:
    """Generate TypeScript type for a field."""
    field_type = field.get("type", "string")
    base_type = TYPE_MAP.get(field_type, "unknown")

    if field_type == "enum":
        values = field.get("values", [])
        if values:
            quoted = [f'"{v}"' for v in values]
            return " | ".join(quoted)
        return "string"
    elif field_type == "array":
        item_type = field.get("itemType", "unknown")
        ts_item_type = TYPE_MAP.get(item_type, "unknown")
        return f"{ts_item_type}[]"

    return base_type


def generate_interface(entity: dict) -> str:
    """Generate TypeScript interface for an entity."""
    name = entity.get("name", "Unknown")
    description = entity.get("description", "")
    fields = entity.get("fields", entity.get("properties", []))

    lines = []

    # JSDoc
    lines.append(f"/**")
    lines.append(f" * {description}")
    lines.append(f" */")
    lines.append(f"export interface {name} {{")

    # Fields
    for field in fields:
        field_name = field.get("name", field.get("id", "unknown"))
        field_type = generate_field_type(field)
        required = field.get("required", False)
        description = field.get("description", "")

        # Optional marker
        optional = "" if required else "?"

        # JSDoc for field
        if description:
            lines.append(f"  /** {description} */")

        lines.append(f"  {field_name}{optional}: {field_type};")

    lines.append("}")
    lines.append("")

    # Generate Create and Update types
    lines.append(f"export type {name}Create = Omit<{name}, 'id' | 'created_at' | 'updated_at'>;")
    lines.append(f"export type {name}Update = Partial<{name}Create>;")
    lines.append("")

    return "\n".join(lines)


def generate_workflow_type(workflow: dict) -> str:
    """Generate TypeScript type for a workflow."""
    workflow_id = workflow.get("id", "unknown")
    name = snake_to_pascal(workflow_id)
    description = workflow.get("description", "")

    lines = []
    lines.append(f"/**")
    lines.append(f" * {description}")
    lines.append(f" */")
    lines.append(f"export interface {name}Workflow {{")
    lines.append(f"  id: '{workflow_id}';")
    lines.append(f"  name: string;")
    lines.append(f"  status: 'pending' | 'running' | 'completed' | 'failed';")
    lines.append(f"  steps: WorkflowStep[];")
    lines.append("}")
    lines.append("")

    return "\n".join(lines)


def generate_signal_types() -> str:
    """Generate TypeScript types for signals."""
    return '''/**
 * Signal event from the event stream.
 */
export interface Signal {
  event_id: string;
  correlation_id: string;
  timestamp: string;
  source: SignalSource;
  type: SignalType;
  payload: Record<string, unknown>;
}

export interface SignalSource {
  system: 'registry' | 'engine' | 'observer';
  component: string;
  node_ref: string;
}

export type SignalType =
  | 'status_change'
  | 'decision'
  | 'alert'
  | 'metric'
  | 'command'
  | 'error';

'''


def generate_genui_types() -> str:
    """Generate TypeScript types for GenUI widgets."""
    return '''/**
 * GenUI widget types.
 */
export type WidgetType =
  | 'ACTION_CARD'
  | 'DATA_TABLE'
  | 'STATUS_BADGE'
  | 'ALERT'
  | 'FORM'
  | 'CHART'
  | 'TIMELINE';

export interface GenUIWidget {
  widget_type: WidgetType;
  props: Record<string, unknown>;
  sandbox?: boolean;
  max_actions?: number;
  callback_url?: string;
}

export interface ActionCardProps {
  title: string;
  description: string;
  actions: ActionButton[];
  severity?: 'info' | 'warning' | 'error' | 'success';
}

export interface ActionButton {
  label: string;
  command: string;
  variant?: 'primary' | 'secondary' | 'danger';
}

export interface DataTableProps {
  title: string;
  columns: TableColumn[];
  data: Record<string, unknown>[];
}

export interface TableColumn {
  key: string;
  label: string;
  type?: 'text' | 'number' | 'date' | 'badge';
}

export interface FormProps {
  title: string;
  fields: FormField[];
  submitLabel?: string;
  onSubmit?: string;
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'checkbox' | 'date';
  required?: boolean;
  options?: { label: string; value: string }[];
}

export interface ChartProps {
  title: string;
  type: 'line' | 'bar' | 'pie' | 'area';
  data: ChartData;
}

export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  color?: string;
}

export interface TimelineProps {
  title: string;
  events: TimelineEvent[];
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  title: string;
  description?: string;
  type?: 'info' | 'success' | 'warning' | 'error';
}

'''


def generate_graph_types() -> str:
    """Generate TypeScript types for graph nodes."""
    return '''/**
 * Business graph types.
 */
export type NodeType =
  | 'WORKFLOW'
  | 'ASSET'
  | 'RULE'
  | 'SKILL'
  | 'ALGORITHM'
  | 'PIPELINE'
  | 'SOURCE';

export interface GraphNode {
  id: string;
  type: NodeType;
  label: string;
  description?: string;
  status?: 'active' | 'inactive' | 'error';
  metadata?: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship: string;
  metadata?: Record<string, unknown>;
}

export interface Graph {
  version: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

'''


def generate_all_types(specs_path: Path, output_path: Path) -> list[Path]:
    """Generate all TypeScript types from specs."""
    specs = load_specs(specs_path)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_files = []

    # Header
    header = f'''/**
 * Auto-generated TypeScript types from specs.
 * DO NOT EDIT - Generated from specs/
 * Generated at: {datetime.now().isoformat()}
 */

'''

    # Entities
    entities_content = header
    entities_content += "// Entity types\n\n"

    for entity in specs.get("entities", {}).get("entities", []):
        entities_content += generate_interface(entity)
        entities_content += "\n"

    entities_file = output_path / "entities.ts"
    entities_file.write_text(entities_content)
    generated_files.append(entities_file)

    # Workflows
    workflows_content = header
    workflows_content += "// Workflow types\n\n"
    workflows_content += '''export interface WorkflowStep {
  id: string;
  action: string;
  next?: string;
  condition?: string;
}

'''

    for workflow in specs.get("workflows", {}).get("workflows", []):
        workflows_content += generate_workflow_type(workflow)

    workflows_file = output_path / "workflows.ts"
    workflows_file.write_text(workflows_content)
    generated_files.append(workflows_file)

    # Signals
    signals_file = output_path / "signals.ts"
    signals_file.write_text(header + generate_signal_types())
    generated_files.append(signals_file)

    # GenUI
    genui_file = output_path / "genui.ts"
    genui_file.write_text(header + generate_genui_types())
    generated_files.append(genui_file)

    # Graph
    graph_file = output_path / "graph.ts"
    graph_file.write_text(header + generate_graph_types())
    generated_files.append(graph_file)

    # Index file
    index_content = '''/**
 * Re-export all generated types.
 */

export * from './entities';
export * from './workflows';
export * from './signals';
export * from './genui';
export * from './graph';
'''

    index_file = output_path / "index.ts"
    index_file.write_text(index_content)
    generated_files.append(index_file)

    return generated_files


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    specs_path = project_root / "specs"
    output_path = project_root / "src" / "types"

    print(f"Generating TypeScript types from {specs_path}")

    generated = generate_all_types(specs_path, output_path)

    if generated:
        print(f"Generated {len(generated)} files:")
        for f in generated:
            print(f"  - {f}")
    else:
        print("No types generated")


if __name__ == "__main__":
    main()
