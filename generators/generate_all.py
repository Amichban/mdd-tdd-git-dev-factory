#!/usr/bin/env python3
"""
Main generator script that runs all generators.

This orchestrates:
1. Model generation from entities.json
2. API generation from entities.json + workflows.json
3. Test generation from entities.json + algorithms.json

Usage:
    python generators/generate_all.py
    python generators/generate_all.py --only models
    python generators/generate_all.py --only api
    python generators/generate_all.py --only tests
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add generators to path
sys.path.insert(0, str(Path(__file__).parent))

from generate_models import generate_all_models
from generate_api import generate_all_apis
from generate_tests import generate_all_tests


def validate_specs(specs_path: Path) -> bool:
    """Validate that spec files exist and are valid JSON."""
    required_files = ["entities.json", "algorithms.json", "workflows.json"]

    for filename in required_files:
        filepath = specs_path / filename
        if not filepath.exists():
            print(f"ERROR: Missing spec file: {filepath}")
            return False

        try:
            import json
            with open(filepath) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {filepath}: {e}")
            return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Generate code from specs")
    parser.add_argument(
        "--only",
        choices=["models", "api", "tests"],
        help="Only run specific generator"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate specs, don't generate"
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    specs_path = project_root / "specs"

    print("=" * 60)
    print("Code Generator")
    print(f"Project: {project_root}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    print()

    # Validate specs
    print("Validating specs...")
    if not validate_specs(specs_path):
        sys.exit(1)
    print("✓ Specs valid")
    print()

    if args.validate_only:
        print("Validation complete (--validate-only)")
        sys.exit(0)

    all_generated = []

    # Generate models
    if args.only is None or args.only == "models":
        print("Generating Pydantic models...")
        output_path = project_root / "src" / "domain" / "models"
        generated = generate_all_models(specs_path, output_path)
        all_generated.extend(generated)
        print(f"✓ Generated {len(generated)} model files")
        print()

    # Generate API
    if args.only is None or args.only == "api":
        print("Generating FastAPI routes...")
        output_path = project_root / "src" / "app" / "api"
        generated = generate_all_apis(specs_path, output_path)
        all_generated.extend(generated)
        print(f"✓ Generated {len(generated)} API files")
        print()

    # Generate tests
    if args.only is None or args.only == "tests":
        print("Generating pytest tests...")
        output_path = project_root / "tests"
        generated = generate_all_tests(specs_path, output_path)
        all_generated.extend(generated)
        print(f"✓ Generated {len(generated)} test files")
        print()

    # Summary
    print("=" * 60)
    print(f"Total files generated: {len(all_generated)}")
    print("=" * 60)

    if all_generated:
        print("\nGenerated files:")
        for f in all_generated:
            rel_path = Path(f).relative_to(project_root)
            print(f"  {rel_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
