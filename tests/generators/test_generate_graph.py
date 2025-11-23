"""Tests for generate_graph.py"""

import pytest
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generators.generate_graph import (
    load_all_specs,
    entity_to_node,
    workflow_to_node,
    algorithm_to_node,
    build_edges,
    generate_graph,
)


class TestEntityToNode:
    def test_basic_entity(self):
        entity = {
            "name": "RawDataSource",
            "description": "Data source configuration",
            "layer": "infrastructure"
        }
        node = entity_to_node(entity)

        assert node["id"] == "asset.raw_data_source.entity"
        assert node["type"] == "ASSET"
        assert node["label"] == "RawDataSource"
        assert node["description"] == "Data source configuration"
        assert node["metadata"]["layer"] == "infrastructure"

    def test_entity_with_different_case(self):
        entity = {
            "name": "MLModel",
            "description": "ML model",
            "layer": "domain"
        }
        node = entity_to_node(entity)
        assert "mlmodel" in node["id"].lower()


class TestWorkflowToNode:
    def test_basic_workflow(self):
        workflow = {
            "id": "data_ingestion",
            "name": "Data Ingestion",
            "description": "Ingest data from sources"
        }
        node = workflow_to_node(workflow)

        assert node["id"] == "wf.data_ingestion.workflow"
        assert node["type"] == "WORKFLOW"
        assert node["label"] == "Data Ingestion"


class TestAlgorithmToNode:
    def test_basic_algorithm(self):
        algorithm = {
            "id": "linear_regression",
            "name": "Linear Regression",
            "description": "Simple linear regression"
        }
        node = algorithm_to_node(algorithm)

        assert node["id"] == "algo.linear_regression.algorithm"
        assert node["type"] == "ALGORITHM"
        assert node["label"] == "Linear Regression"


class TestBuildEdges:
    def test_empty_specs(self):
        specs = {}
        nodes = []
        edges = build_edges(specs, nodes)
        assert edges == []

    def test_workflow_step_edges(self):
        specs = {
            "workflows": {
                "workflows": [
                    {
                        "id": "test_workflow",
                        "steps": [
                            {"id": "step1", "action": "test_action"},
                            {"id": "step2", "action": "test_action2"}
                        ]
                    }
                ]
            }
        }
        nodes = [
            {"id": "wf.test_workflow.workflow", "type": "WORKFLOW"}
        ]

        edges = build_edges(specs, nodes)
        assert len(edges) > 0


class TestGenerateGraph:
    def test_generates_graph_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)

            specs = {
                "entities": {
                    "entities": [
                        {
                            "name": "TestEntity",
                            "description": "Test",
                            "layer": "domain"
                        }
                    ]
                },
                "workflows": {"workflows": []},
                "algorithms": {"algorithms": []}
            }

            generated = generate_graph(specs, output_path)

            assert len(generated) == 1
            graph_file = output_path / "graph.json"
            assert graph_file.exists()

            with open(graph_file) as f:
                graph = json.load(f)

            assert "version" in graph
            assert "nodes" in graph
            assert "edges" in graph
            assert len(graph["nodes"]) == 1


class TestLoadAllSpecs:
    def test_loads_all_spec_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            specs_path = Path(tmpdir)

            # Create minimal spec files
            (specs_path / "entities.json").write_text(json.dumps({"entities": []}))
            (specs_path / "workflows.json").write_text(json.dumps({"workflows": []}))
            (specs_path / "algorithms.json").write_text(json.dumps({"algorithms": []}))

            specs = load_all_specs(specs_path)

            assert "entities" in specs
            assert "workflows" in specs
            assert "algorithms" in specs

    def test_handles_missing_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            specs_path = Path(tmpdir)
            specs = load_all_specs(specs_path)

            # Should return empty dict for missing files
            assert specs == {} or all(v == {} for v in specs.values())
