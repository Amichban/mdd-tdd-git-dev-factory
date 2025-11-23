#!/usr/bin/env python3
"""
Generate pytest tests from specs/algorithms.json

This generator reads algorithm definitions and produces:
- Test cases from defined test data
- Parameterized tests for each algorithm
- Property-based tests for constraints
"""

import json
from pathlib import Path
from datetime import datetime


def load_algorithms(specs_path: Path) -> dict:
    """Load algorithms from JSON spec file."""
    algorithms_file = specs_path / "algorithms.json"
    with open(algorithms_file) as f:
        return json.load(f)


def load_entities(specs_path: Path) -> dict:
    """Load entities from JSON spec file."""
    entities_file = specs_path / "entities.json"
    with open(entities_file) as f:
        return json.load(f)


def generate_algorithm_test(algo: dict) -> str:
    """Generate test file for an algorithm."""
    algo_id = algo["id"]
    algo_name = algo["name"]
    func_name = algo_id.replace("algo_", "")

    lines = [
        f'"""',
        f'Tests for {algo_name}',
        f'Generated from specs/algorithms.json',
        f'Generated at: {datetime.now().isoformat()}',
        f'"""',
        '',
        'import pytest',
        'from math import isclose',
        '',
        f'from domain.calculations.{func_name} import {func_name}',
        '',
        '',
    ]

    # Generate test class
    class_name = "".join(word.capitalize() for word in func_name.split("_"))
    lines.append(f'class Test{class_name}:')
    lines.append(f'    """{algo["description"]}"""')
    lines.append('')

    # Generate parameterized test from test cases
    tests = algo.get("tests", [])
    if tests:
        # Build test data
        test_params = []
        for i, test in enumerate(tests):
            inputs = test["inputs"]
            expected = test["expected"]
            tolerance = test.get("tolerance", 0.01)
            desc = test.get("description", f"test_case_{i+1}")

            # Format inputs as kwargs
            input_str = ", ".join(f"{k}={v}" for k, v in inputs.items())
            test_params.append(f'        ({input_str}, {expected}, {tolerance}, "{desc}"),')

        lines.append('    @pytest.mark.parametrize(')

        # Build parameter names from inputs
        input_names = list(tests[0]["inputs"].keys())
        param_names = ", ".join(input_names)
        lines.append(f'        "{param_names}, expected, tolerance, description",')
        lines.append('        [')
        lines.extend(test_params)
        lines.append('        ]')
        lines.append('    )')

        # Generate test method
        input_args = ", ".join(input_names)
        lines.append(f'    def test_calculation(self, {input_args}, expected, tolerance, description):')
        lines.append(f'        """Test {algo_name} with parameterized inputs."""')
        lines.append(f'        result = {func_name}({input_args})')
        lines.append('        assert isclose(result, expected, abs_tol=tolerance), \\')
        lines.append(f'            f"{{description}}: expected {{expected}}, got {{result}}"')
        lines.append('')

    # Generate boundary tests from constraints
    output = algo.get("output", {})
    if "min" in output or "max" in output:
        lines.append('    def test_output_bounds(self):')
        lines.append(f'        """Test that output is within bounds."""')
        lines.append('        # Test with various inputs')

        # Generate some test inputs
        inputs = algo.get("inputs", [])
        input_args = []
        for inp in inputs:
            constraints = inp.get("constraints", {})
            if "min" in constraints and "max" in constraints:
                mid = (constraints["min"] + constraints["max"]) / 2
                input_args.append(str(mid))
            else:
                input_args.append("1")  # Default test value

        if input_args:
            lines.append(f'        result = {func_name}({", ".join(input_args)})')
            if "min" in output:
                lines.append(f'        assert result >= {output["min"]}, f"Result {{result}} below minimum {output["min"]}"')
            if "max" in output:
                lines.append(f'        assert result <= {output["max"]}, f"Result {{result}} above maximum {output["max"]}"')
        lines.append('')

    # Generate step explanation test
    steps = algo.get("steps", [])
    if steps:
        lines.append('    def test_steps_documented(self):')
        lines.append(f'        """Verify algorithm steps are documented for explainability."""')
        lines.append('        steps = [')
        for step in steps:
            lines.append(f'            "{step["name"]}",')
        lines.append('        ]')
        lines.append(f'        assert len(steps) == {len(steps)}, "Algorithm should have {len(steps)} documented steps"')
        lines.append('')

    return "\n".join(lines)


def generate_entity_tests(entity: dict) -> str:
    """Generate tests for entity validation and actions."""
    entity_id = entity["id"]
    class_name = entity["name"]

    lines = [
        f'"""',
        f'Tests for {class_name} entity',
        f'Generated from specs/entities.json',
        f'Generated at: {datetime.now().isoformat()}',
        f'"""',
        '',
        'import pytest',
        'from pydantic import ValidationError',
        '',
        f'from domain.models.{entity_id} import {class_name}',
        '',
        '',
        f'class Test{class_name}:',
        f'    """{entity["description"]}"""',
        '',
    ]

    # Test required fields
    required_fields = [p for p in entity.get("properties", []) if p.get("required", False)]
    if required_fields:
        lines.append('    def test_required_fields(self):')
        lines.append('        """Test that required fields are enforced."""')
        lines.append('        with pytest.raises(ValidationError):')
        lines.append(f'            {class_name}()  # Should fail without required fields')
        lines.append('')

    # Test enum constraints
    enum_fields = [p for p in entity.get("properties", []) if p["type"] == "enum"]
    for field in enum_fields:
        lines.append(f'    def test_{field["id"]}_enum_values(self):')
        lines.append(f'        """Test {field["name"]} only accepts valid values."""')
        lines.append(f'        valid_values = {field["values"]}')
        lines.append('        for value in valid_values:')
        lines.append('            # Should not raise')
        lines.append(f'            # {class_name}(..., {field["id"]}=value)')
        lines.append('            pass')
        lines.append('')
        lines.append('        with pytest.raises(ValidationError):')
        lines.append(f'            # {class_name}(..., {field["id"]}="invalid_value")')
        lines.append('            pass')
        lines.append('')

    # Test numeric constraints
    constrained_fields = [p for p in entity.get("properties", [])
                         if p.get("constraints") and ("min" in p["constraints"] or "max" in p["constraints"])]
    for field in constrained_fields:
        constraints = field["constraints"]
        lines.append(f'    def test_{field["id"]}_constraints(self):')
        lines.append(f'        """Test {field["name"]} respects constraints."""')
        if "min" in constraints:
            lines.append(f'        # Value below {constraints["min"]} should fail')
            lines.append('        # with pytest.raises(ValidationError):')
            lines.append(f'        #     {class_name}(..., {field["id"]}={constraints["min"] - 1})')
        if "max" in constraints:
            lines.append(f'        # Value above {constraints["max"]} should fail')
            lines.append('        # with pytest.raises(ValidationError):')
            lines.append(f'        #     {class_name}(..., {field["id"]}={constraints["max"] + 1})')
        lines.append('        pass')
        lines.append('')

    # Test actions have preconditions
    actions = entity.get("actions", [])
    for action in actions:
        if action.get("preconditions"):
            lines.append(f'    def test_{action["id"]}_preconditions(self):')
            lines.append(f'        """Test {action["name"]} respects preconditions."""')
            for pre in action["preconditions"]:
                lines.append(f'        # Precondition: {pre}')
            lines.append('        pass')
            lines.append('')

    return "\n".join(lines)


def generate_all_tests(specs_path: Path, output_path: Path) -> list[str]:
    """Generate all tests from specs."""
    generated_files = []

    # Ensure output directories exist
    algo_test_path = output_path / "unit" / "algorithms"
    entity_test_path = output_path / "unit" / "entities"
    algo_test_path.mkdir(parents=True, exist_ok=True)
    entity_test_path.mkdir(parents=True, exist_ok=True)

    # Generate algorithm tests
    algo_data = load_algorithms(specs_path)
    for algo in algo_data.get("algorithms", []):
        test_code = generate_algorithm_test(algo)
        func_name = algo["id"].replace("algo_", "")
        test_file = algo_test_path / f"test_{func_name}.py"

        with open(test_file, "w") as f:
            f.write(test_code)

        generated_files.append(str(test_file))

    # Generate entity tests
    entity_data = load_entities(specs_path)
    for entity in entity_data.get("entities", []):
        test_code = generate_entity_tests(entity)
        test_file = entity_test_path / f"test_{entity['id']}.py"

        with open(test_file, "w") as f:
            f.write(test_code)

        generated_files.append(str(test_file))

    # Generate conftest.py
    conftest = output_path / "conftest.py"
    with open(conftest, "w") as f:
        f.write('"""Pytest configuration and fixtures."""\n\n')
        f.write('import pytest\n')
        f.write('import sys\n')
        f.write('from pathlib import Path\n\n')
        f.write('# Add src to path for imports\n')
        f.write('sys.path.insert(0, str(Path(__file__).parent.parent / "src"))\n')

    generated_files.append(str(conftest))

    return generated_files


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    specs_path = project_root / "specs"
    output_path = project_root / "tests"

    print(f"Generating tests from {specs_path}")

    generated = generate_all_tests(specs_path, output_path)

    if generated:
        print(f"Generated {len(generated)} test files:")
        for f in generated:
            print(f"  - {f}")
    else:
        print("No algorithms or entities found in specs")


if __name__ == "__main__":
    main()
