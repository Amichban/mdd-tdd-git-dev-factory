"""
Runtime schema validation service.

Validates specs and data against JSON schemas at runtime.
"""

import json
from pathlib import Path
from typing import Any
from jsonschema import validate, ValidationError, Draft7Validator
from jsonschema.exceptions import SchemaError


class SchemaValidator:
    """Validates data against JSON schemas."""

    def __init__(self, schema_dir: Path = None):
        """Initialize validator with schema directory."""
        if schema_dir is None:
            schema_dir = Path(__file__).parent.parent / "specs" / "schema"
        self.schema_dir = schema_dir
        self._schema_cache: dict[str, dict] = {}

    def load_schema(self, schema_name: str) -> dict:
        """Load a schema by name (without extension)."""
        if schema_name in self._schema_cache:
            return self._schema_cache[schema_name]

        schema_file = self.schema_dir / f"{schema_name}.schema.json"
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema not found: {schema_file}")

        with open(schema_file) as f:
            schema = json.load(f)

        self._schema_cache[schema_name] = schema
        return schema

    def validate(self, data: dict, schema_name: str) -> tuple[bool, list[str]]:
        """
        Validate data against a schema.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        try:
            schema = self.load_schema(schema_name)
            validate(instance=data, schema=schema)
            return True, []
        except ValidationError as e:
            errors = [self._format_error(e)]
            # Collect all errors
            validator = Draft7Validator(schema)
            for error in validator.iter_errors(data):
                if error.message not in errors:
                    errors.append(self._format_error(error))
            return False, errors
        except SchemaError as e:
            return False, [f"Invalid schema: {e.message}"]
        except FileNotFoundError as e:
            return False, [str(e)]

    def validate_entity(self, entity: dict) -> tuple[bool, list[str]]:
        """Validate an entity against entity schema."""
        return self.validate({"entities": [entity]}, "entity")

    def validate_workflow(self, workflow: dict) -> tuple[bool, list[str]]:
        """Validate a workflow against workflow schema."""
        return self.validate({"workflows": [workflow]}, "workflow")

    def validate_algorithm(self, algorithm: dict) -> tuple[bool, list[str]]:
        """Validate an algorithm against algorithm schema."""
        return self.validate({"algorithms": [algorithm]}, "algorithm")

    def validate_signal(self, signal: dict) -> tuple[bool, list[str]]:
        """Validate a signal against signal schema."""
        return self.validate(signal, "signal")

    def validate_graph_node(self, node: dict) -> tuple[bool, list[str]]:
        """Validate a graph node against graph schema."""
        return self.validate({"nodes": [node], "edges": []}, "graph")

    def validate_genui_widget(self, widget: dict) -> tuple[bool, list[str]]:
        """Validate a GenUI widget against genui schema."""
        return self.validate(widget, "genui")

    def validate_9box(self, spec: dict) -> tuple[bool, list[str]]:
        """Validate a 9-box specification."""
        return self.validate(spec, "9box")

    def validate_all_specs(self, specs_dir: Path = None) -> dict[str, tuple[bool, list[str]]]:
        """
        Validate all spec files in a directory.

        Returns:
            Dict mapping filename to (is_valid, errors)
        """
        if specs_dir is None:
            specs_dir = self.schema_dir.parent

        results = {}
        spec_files = {
            "entities.json": "entity",
            "workflows.json": "workflow",
            "algorithms.json": "algorithm",
            "workbenches.json": "workbench",
            "roles.json": "roles"
        }

        for filename, schema_name in spec_files.items():
            filepath = specs_dir / filename
            if filepath.exists():
                try:
                    with open(filepath) as f:
                        data = json.load(f)
                    results[filename] = self.validate(data, schema_name)
                except json.JSONDecodeError as e:
                    results[filename] = (False, [f"Invalid JSON: {e}"])
            else:
                results[filename] = (True, [])  # Missing file is OK

        return results

    def _format_error(self, error: ValidationError) -> str:
        """Format a validation error message."""
        path = ".".join(str(p) for p in error.absolute_path)
        if path:
            return f"{path}: {error.message}"
        return error.message


# Global validator instance
_validator = None


def get_validator() -> SchemaValidator:
    """Get the global schema validator instance."""
    global _validator
    if _validator is None:
        _validator = SchemaValidator()
    return _validator


def validate_spec(data: dict, schema_name: str) -> tuple[bool, list[str]]:
    """Convenience function to validate data against a schema."""
    return get_validator().validate(data, schema_name)


def validate_signal(signal: dict) -> tuple[bool, list[str]]:
    """Validate a signal event."""
    return get_validator().validate_signal(signal)


def validate_genui(widget: dict) -> tuple[bool, list[str]]:
    """Validate a GenUI widget."""
    return get_validator().validate_genui_widget(widget)
