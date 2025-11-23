#!/usr/bin/env python3
"""
Generate business graph from specs.
Builds typed graph nodes and edges conforming to Graph Contract.
"""

import json
from pathlib import Path
from datetime import datetime


def entity_to_node(entity: dict) -> dict:
    """Convert entity spec to graph node."""
    name = entity['name']
    name_lower = name.lower()

    return {
        'id': f"asset.entity.{name_lower}",
        'type': 'ASSET',
        'label': name,
        'metadata': {
            'owner': entity.get('owner', 'System'),
            'business_criticality': entity.get('criticality', 'MEDIUM'),
            'fields_count': len(entity.get('fields', [])),
        },
        'status_source': f"hook.entity.{name_lower}_status"
    }


def algorithm_to_node(algorithm: dict) -> dict:
    """Convert algorithm spec to graph node."""
    algo_id = algorithm.get('id', algorithm.get('name', 'unknown'))
    name = algorithm.get('name', algo_id)

    return {
        'id': f"algo.compute.{algo_id}",
        'type': 'ALGORITHM',
        'label': name,
        'metadata': {
            'owner': algorithm.get('owner', 'System'),
            'business_criticality': algorithm.get('criticality', 'MEDIUM'),
        }
    }


def workflow_to_node(workflow: dict) -> dict:
    """Convert workflow spec to graph node."""
    wf_id = workflow.get('id', workflow.get('name', 'unknown'))
    name = workflow.get('name', wf_id)

    return {
        'id': f"wf.process.{wf_id}",
        'type': 'WORKFLOW',
        'label': name,
        'metadata': {
            'owner': workflow.get('owner', 'System'),
            'business_criticality': workflow.get('criticality', 'HIGH'),
            'sla': workflow.get('sla', 'None'),
        }
    }


def skill_to_node(skill: dict) -> dict:
    """Convert skill to graph node."""
    skill_id = skill.get('id', skill.get('name', 'unknown'))
    name = skill.get('name', skill_id)

    return {
        'id': f"skill.agent.{skill_id}",
        'type': 'SKILL',
        'label': name,
        'metadata': {
            'owner': 'Agent',
            'business_criticality': 'MEDIUM',
        }
    }


def build_edges(specs: dict, nodes: list[dict]) -> list[dict]:
    """Build edges between nodes based on relationships."""
    edges = []
    node_ids = {n['id'] for n in nodes}

    # Entity relationships
    for entity in specs.get('entities', {}).get('entities', []):
        entity_id = f"asset.entity.{entity['name'].lower()}"

        # Check for foreign keys / relationships
        for field in entity.get('fields', []):
            if field.get('type') == 'uuid' and field.get('references'):
                ref_entity = field['references'].lower()
                ref_id = f"asset.entity.{ref_entity}"
                if ref_id in node_ids:
                    edges.append({
                        'source': entity_id,
                        'target': ref_id,
                        'relation': 'DEPENDS_ON',
                        'semantics': f"{field['name']} references {ref_entity}"
                    })

    # Workflow -> Entity relationships
    for workflow in specs.get('workflows', {}).get('workflows', []):
        wf_id = f"wf.process.{workflow.get('id', workflow.get('name', 'unknown'))}"

        # Workflows that produce entities
        for produces in workflow.get('produces', []):
            entity_id = f"asset.entity.{produces.lower()}"
            if entity_id in node_ids:
                edges.append({
                    'source': wf_id,
                    'target': entity_id,
                    'relation': 'PRODUCES',
                    'semantics': f"Workflow produces {produces}"
                })

        # Workflows that consume entities
        for consumes in workflow.get('consumes', []):
            entity_id = f"asset.entity.{consumes.lower()}"
            if entity_id in node_ids:
                edges.append({
                    'source': wf_id,
                    'target': entity_id,
                    'relation': 'CONSUMES',
                    'semantics': f"Workflow consumes {consumes}"
                })

    return edges


def generate_graph(specs: dict, output_dir: Path) -> list[Path]:
    """Generate business graph from all specs."""
    nodes = []

    # Convert entities to nodes
    for entity in specs.get('entities', {}).get('entities', []):
        nodes.append(entity_to_node(entity))

    # Convert algorithms to nodes
    for algorithm in specs.get('algorithms', {}).get('algorithms', []):
        nodes.append(algorithm_to_node(algorithm))

    # Convert workflows to nodes
    for workflow in specs.get('workflows', {}).get('workflows', []):
        nodes.append(workflow_to_node(workflow))

    # Build edges
    edges = build_edges(specs, nodes)

    # Create graph document
    graph = {
        'version': '2.0',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'nodes': nodes,
        'edges': edges
    }

    # Write graph to file
    graph_dir = output_dir / 'data'
    graph_dir.mkdir(parents=True, exist_ok=True)

    graph_path = graph_dir / 'graph.json'
    with open(graph_path, 'w') as f:
        json.dump(graph, f, indent=2)

    print(f"  ✓ {graph_path} ({len(nodes)} nodes, {len(edges)} edges)")

    return [graph_path]
