"""Tests for generate_components.py"""

import pytest
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generators.generate_components import (
    load_workbenches,
    generate_workbench_component,
    generate_all_components,
)


class TestLoadWorkbenches:
    def test_loads_valid_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            specs_path = Path(tmpdir)
            workbenches_data = {
                "version": "1.0.0",
                "workbenches": [
                    {"id": "test", "name": "Test Workbench"}
                ]
            }

            with open(specs_path / "workbenches.json", "w") as f:
                json.dump(workbenches_data, f)

            result = load_workbenches(specs_path)
            assert result["version"] == "1.0.0"
            assert len(result["workbenches"]) == 1

    def test_raises_on_missing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            specs_path = Path(tmpdir)
            with pytest.raises(FileNotFoundError):
                load_workbenches(specs_path)


class TestGenerateWorkbenchComponent:
    def test_generates_tsx_component(self):
        workbench = {
            "id": "data_engineer",
            "name": "Data Engineer Workbench",
            "description": "Workbench for data engineers",
            "sections": {
                "header": {"title": "Data Engineer"},
                "canvas_read": {"widgets": []},
                "canvas_write": {"widgets": []},
                "tools": {"items": []}
            }
        }

        result = generate_workbench_component(workbench)

        assert "export default function DataEngineerWorkbench" in result
        assert "Data Engineer Workbench" in result
        assert "'use client'" in result
        assert "import React" in result

    def test_handles_minimal_workbench(self):
        workbench = {
            "id": "simple",
            "name": "Simple Workbench",
            "description": "Basic workbench",
            "sections": {}
        }

        result = generate_workbench_component(workbench)
        assert "SimpleWorkbench" in result


class TestGenerateAllComponents:
    def test_generates_workbench_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            specs_path = Path(tmpdir)
            output_path = Path(tmpdir) / "components"

            workbenches_data = {
                "version": "1.0.0",
                "workbenches": [
                    {
                        "id": "test_workbench",
                        "name": "Test Workbench",
                        "description": "For testing",
                        "sections": {
                            "header": {"title": "Test"}
                        }
                    }
                ]
            }

            with open(specs_path / "workbenches.json", "w") as f:
                json.dump(workbenches_data, f)

            generated = generate_all_components(specs_path, output_path)

            assert len(generated) >= 1
            assert output_path.exists()

    def test_creates_index_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            specs_path = Path(tmpdir)
            output_path = Path(tmpdir) / "components"

            workbenches_data = {
                "version": "1.0.0",
                "workbenches": [
                    {
                        "id": "wb1",
                        "name": "Workbench 1",
                        "description": "First",
                        "sections": {}
                    },
                    {
                        "id": "wb2",
                        "name": "Workbench 2",
                        "description": "Second",
                        "sections": {}
                    }
                ]
            }

            with open(specs_path / "workbenches.json", "w") as f:
                json.dump(workbenches_data, f)

            generate_all_components(specs_path, output_path)

            index_file = output_path / "index.ts"
            assert index_file.exists()

            content = index_file.read_text()
            assert "Wb1Workbench" in content or "export" in content
