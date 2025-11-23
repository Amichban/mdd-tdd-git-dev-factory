"""
Graph Builder Service.
Builds and serves the business graph conforming to Graph Contract.
"""

import json
from pathlib import Path
from typing import Optional


class GraphBuilder:
    """Build and query the business graph."""

    def __init__(self, graph_path: Path = Path('src/data/graph.json')):
        self.graph_path = graph_path
        self._graph: Optional[dict] = None

    def load(self) -> dict:
        """Load graph from file."""
        if self._graph is None:
            if self.graph_path.exists():
                with open(self.graph_path) as f:
                    self._graph = json.load(f)
            else:
                self._graph = {'version': '2.0', 'nodes': [], 'edges': []}
        return self._graph

    def get_graph(self) -> dict:
        """Get the full graph."""
        return self.load()

    def get_node(self, node_id: str) -> Optional[dict]:
        """Get a specific node by ID."""
        graph = self.load()
        for node in graph.get('nodes', []):
            if node['id'] == node_id:
                return node
        return None

    def get_nodes_by_type(self, node_type: str) -> list[dict]:
        """Get all nodes of a specific type."""
        graph = self.load()
        return [n for n in graph.get('nodes', []) if n['type'] == node_type]

    def get_edges_for_node(self, node_id: str) -> dict:
        """Get all edges connected to a node."""
        graph = self.load()
        incoming = []
        outgoing = []

        for edge in graph.get('edges', []):
            if edge['source'] == node_id:
                outgoing.append(edge)
            if edge['target'] == node_id:
                incoming.append(edge)

        return {'incoming': incoming, 'outgoing': outgoing}

    def get_lineage(self, node_id: str, direction: str = 'upstream') -> list[str]:
        """Get lineage (upstream or downstream) for a node."""
        graph = self.load()
        visited = set()
        result = []

        def traverse(current_id: str):
            if current_id in visited:
                return
            visited.add(current_id)

            for edge in graph.get('edges', []):
                if direction == 'upstream' and edge['target'] == current_id:
                    result.append(edge['source'])
                    traverse(edge['source'])
                elif direction == 'downstream' and edge['source'] == current_id:
                    result.append(edge['target'])
                    traverse(edge['target'])

        traverse(node_id)
        return result

    def search_nodes(self, query: str) -> list[dict]:
        """Search nodes by label or ID."""
        graph = self.load()
        query_lower = query.lower()
        return [
            n for n in graph.get('nodes', [])
            if query_lower in n['id'].lower() or query_lower in n['label'].lower()
        ]

    def get_stats(self) -> dict:
        """Get graph statistics."""
        graph = self.load()
        nodes = graph.get('nodes', [])
        edges = graph.get('edges', [])

        type_counts = {}
        for node in nodes:
            node_type = node['type']
            type_counts[node_type] = type_counts.get(node_type, 0) + 1

        relation_counts = {}
        for edge in edges:
            relation = edge['relation']
            relation_counts[relation] = relation_counts.get(relation, 0) + 1

        return {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'nodes_by_type': type_counts,
            'edges_by_relation': relation_counts,
        }


# Singleton instance
_graph_builder: Optional[GraphBuilder] = None


def get_graph_builder() -> GraphBuilder:
    """Get the graph builder singleton."""
    global _graph_builder
    if _graph_builder is None:
        _graph_builder = GraphBuilder()
    return _graph_builder
