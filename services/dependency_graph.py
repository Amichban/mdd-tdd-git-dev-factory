"""
Dependency Graph Service

Tracks relationships between entities and determines:
- What entities a change affects
- Whether changes can be parallelized
- Dependency ordering for changes
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class EntityNode:
    """Node in the dependency graph."""
    id: str
    name: str
    dependencies: set[str]  # Entities this one depends on
    dependents: set[str]    # Entities that depend on this one


class DependencyGraph:
    """Tracks entity dependencies for conflict detection and parallelization."""

    def __init__(self, specs_path: Path):
        self.specs_path = specs_path
        self.nodes: dict[str, EntityNode] = {}
        self.build_from_specs()

    def build_from_specs(self):
        """Build dependency graph from specs/entities.json."""
        entities_file = self.specs_path / "entities.json"

        if not entities_file.exists():
            return

        with open(entities_file) as f:
            data = json.load(f)

        # First pass: create nodes
        for entity in data.get("entities", []):
            entity_id = entity["id"]
            self.nodes[entity_id] = EntityNode(
                id=entity_id,
                name=entity["name"],
                dependencies=set(),
                dependents=set()
            )

        # Second pass: build relationships
        for entity in data.get("entities", []):
            entity_id = entity["id"]

            for rel in entity.get("relationships", []):
                target = rel["targetEntity"]

                # This entity depends on target
                if entity_id in self.nodes and target in self.nodes:
                    self.nodes[entity_id].dependencies.add(target)
                    self.nodes[target].dependents.add(entity_id)

            # Check for calculated fields that depend on algorithms
            for prop in entity.get("properties", []):
                if "calculatedBy" in prop:
                    # Track algorithm dependencies if needed
                    pass

    def get_dependencies(self, entity_id: str) -> set[str]:
        """Get all entities that this entity depends on (direct and transitive)."""
        if entity_id not in self.nodes:
            return set()

        visited = set()
        to_visit = [entity_id]

        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)

            if current in self.nodes:
                for dep in self.nodes[current].dependencies:
                    if dep not in visited:
                        to_visit.append(dep)

        visited.remove(entity_id)
        return visited

    def get_dependents(self, entity_id: str) -> set[str]:
        """Get all entities that depend on this entity (direct and transitive)."""
        if entity_id not in self.nodes:
            return set()

        visited = set()
        to_visit = [entity_id]

        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)

            if current in self.nodes:
                for dep in self.nodes[current].dependents:
                    if dep not in visited:
                        to_visit.append(dep)

        visited.remove(entity_id)
        return visited

    def get_impact(self, entity_id: str) -> set[str]:
        """Get all entities affected by a change to this entity."""
        # A change affects the entity itself and all its dependents
        impact = {entity_id}
        impact.update(self.get_dependents(entity_id))
        return impact

    def can_parallelize(self, change_a: str, change_b: str) -> bool:
        """
        Determine if two changes can be worked on in parallel.

        Changes can be parallelized if their impact sets don't overlap.
        """
        impact_a = self.get_impact(change_a)
        impact_b = self.get_impact(change_b)

        # No overlap = safe to parallelize
        return len(impact_a & impact_b) == 0

    def find_conflicts(
        self,
        entity_id: str,
        in_flight_entities: list[str]
    ) -> list[str]:
        """
        Find conflicts between a new change and in-flight changes.

        Returns list of entity IDs that conflict.
        """
        impact = self.get_impact(entity_id)
        conflicts = []

        for in_flight in in_flight_entities:
            in_flight_impact = self.get_impact(in_flight)
            overlap = impact & in_flight_impact

            if overlap:
                conflicts.append(in_flight)

        return conflicts

    def get_change_order(self, entities: list[str]) -> list[str]:
        """
        Get the order in which changes should be applied.

        Uses topological sort based on dependencies.
        """
        # Build in-degree map
        in_degree = {e: 0 for e in entities}
        graph = {e: [] for e in entities}

        for entity in entities:
            if entity in self.nodes:
                for dep in self.nodes[entity].dependencies:
                    if dep in entities:
                        graph[dep].append(entity)
                        in_degree[entity] += 1

        # Topological sort using Kahn's algorithm
        queue = [e for e in entities if in_degree[e] == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for dependent in graph.get(current, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check for cycles
        if len(result) != len(entities):
            # Cycle detected, return original order
            return entities

        return result

    def visualize_mermaid(self) -> str:
        """Generate Mermaid diagram of the dependency graph."""
        lines = ["graph TD"]

        for entity_id, node in self.nodes.items():
            # Node definition
            lines.append(f"    {entity_id}[{node.name}]")

            # Edges (dependencies)
            for dep in node.dependencies:
                lines.append(f"    {dep} --> {entity_id}")

        return "\n".join(lines)

    def get_entity_info(self, entity_id: str) -> Optional[dict]:
        """Get information about an entity's dependencies."""
        if entity_id not in self.nodes:
            return None

        node = self.nodes[entity_id]
        return {
            "id": node.id,
            "name": node.name,
            "depends_on": list(node.dependencies),
            "depended_by": list(node.dependents),
            "all_dependencies": list(self.get_dependencies(entity_id)),
            "all_dependents": list(self.get_dependents(entity_id)),
            "total_impact": len(self.get_impact(entity_id))
        }

    def analyze_change_risk(self, entity_id: str) -> str:
        """Analyze the risk level of changing an entity."""
        if entity_id not in self.nodes:
            return "unknown"

        impact_size = len(self.get_impact(entity_id))

        if impact_size == 1:
            return "low"
        elif impact_size <= 3:
            return "medium"
        else:
            return "high"
