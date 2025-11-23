"""Shared fixtures for generator tests."""

import pytest
import tempfile
import json
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_entity():
    """Provide a sample entity for testing."""
    return {
        "id": "test_entity",
        "name": "TestEntity",
        "description": "A test entity for unit tests",
        "layer": "domain",
        "properties": [
            {"id": "name", "type": "string", "required": True},
            {"id": "count", "type": "integer", "required": False, "default": 0},
            {"id": "status", "type": "enum", "values": ["active", "inactive"], "required": True},
            {"id": "created_at", "type": "datetime", "required": True}
        ],
        "api": {
            "endpoints": ["list", "get", "create", "update", "delete"]
        }
    }


@pytest.fixture
def sample_workflow():
    """Provide a sample workflow for testing."""
    return {
        "id": "test_workflow",
        "name": "Test Workflow",
        "description": "A test workflow",
        "steps": [
            {"id": "step1", "action": "prepare", "next": "step2"},
            {"id": "step2", "action": "execute", "next": "step3"},
            {"id": "step3", "action": "cleanup"}
        ]
    }


@pytest.fixture
def sample_workbench():
    """Provide a sample workbench for testing."""
    return {
        "id": "test_workbench",
        "name": "Test Workbench",
        "description": "A test workbench",
        "sections": {
            "header": {
                "title": "Test Workbench",
                "subtitle": "For testing"
            },
            "canvas_read": {
                "widgets": [
                    {"type": "DATA_TABLE", "title": "Test Data"}
                ]
            },
            "tools": {
                "items": [
                    {"id": "tool1", "label": "Tool 1", "action": "test"}
                ]
            }
        }
    }


@pytest.fixture
def specs_dir(temp_dir, sample_entity, sample_workflow, sample_workbench):
    """Create a specs directory with sample spec files."""
    specs_path = temp_dir / "specs"
    specs_path.mkdir()

    # Create entities.json
    entities_data = {
        "version": "1.0.0",
        "entities": [sample_entity]
    }
    (specs_path / "entities.json").write_text(json.dumps(entities_data))

    # Create workflows.json
    workflows_data = {
        "version": "1.0.0",
        "workflows": [sample_workflow]
    }
    (specs_path / "workflows.json").write_text(json.dumps(workflows_data))

    # Create workbenches.json
    workbenches_data = {
        "version": "1.0.0",
        "workbenches": [sample_workbench]
    }
    (specs_path / "workbenches.json").write_text(json.dumps(workbenches_data))

    # Create algorithms.json
    algorithms_data = {
        "version": "1.0.0",
        "algorithms": []
    }
    (specs_path / "algorithms.json").write_text(json.dumps(algorithms_data))

    return specs_path
