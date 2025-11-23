#!/usr/bin/env python3
"""
Unified spec compiler.

Compiles all specs and generates all artifacts in one pass.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generators.generate_models import generate_all_models
from generators.generate_routes import generate_routes
from generators.generate_graph import generate_graph, load_all_specs
from generators.generate_components import generate_all_components
from generators.generate_types import generate_all_types


class SpecCompiler:
    """Unified compiler for all specs."""

    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent
        self.project_root = project_root
        self.specs_path = project_root / "specs"
        self.src_path = project_root / "src"

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "generated": [],
            "errors": [],
            "warnings": []
        }

    def compile_all(self, verbose: bool = True) -> dict:
        """Compile all specs and generate all artifacts."""
        if verbose:
            print("=" * 60)
            print("  Dev Platform Spec Compiler")
            print("=" * 60)
            print()

        # Load all specs first
        specs = load_all_specs(self.specs_path)

        # Run each generator
        self._run_generator(
            "models",
            lambda: generate_all_models(
                self.specs_path,
                self.src_path / "domain" / "models"
            ),
            verbose
        )

        self._run_generator(
            "routes",
            lambda: generate_routes(specs, self.src_path),
            verbose
        )

        self._run_generator(
            "graph",
            lambda: generate_graph(specs, self.src_path / "data"),
            verbose
        )

        self._run_generator(
            "components",
            lambda: generate_all_components(
                self.specs_path,
                self.src_path / "components" / "workbenches"
            ),
            verbose
        )

        self._run_generator(
            "types",
            lambda: generate_all_types(
                self.specs_path,
                self.src_path / "types"
            ),
            verbose
        )

        # Summary
        if verbose:
            print()
            print("=" * 60)
            print("  Compilation Summary")
            print("=" * 60)
            print(f"  Generated: {len(self.results['generated'])} files")
            print(f"  Errors: {len(self.results['errors'])}")
            print(f"  Warnings: {len(self.results['warnings'])}")
            print()

        return self.results

    def _run_generator(self, name: str, generator_fn, verbose: bool):
        """Run a generator and capture results."""
        if verbose:
            print(f"Generating {name}...")

        try:
            generated = generator_fn()
            if generated:
                self.results["generated"].extend(
                    str(f) for f in generated
                )
                if verbose:
                    print(f"  ✓ Generated {len(generated)} files")
        except Exception as e:
            self.results["errors"].append({
                "generator": name,
                "error": str(e)
            })
            if verbose:
                print(f"  ✗ Error: {e}")

    def validate_specs(self, verbose: bool = True) -> bool:
        """Validate all specs before compilation."""
        from services.schema_validator import get_validator

        if verbose:
            print("Validating specs...")

        validator = get_validator()
        results = validator.validate_all_specs(self.specs_path)

        all_valid = True
        for filename, (is_valid, errors) in results.items():
            if not is_valid:
                all_valid = False
                self.results["errors"].append({
                    "file": filename,
                    "errors": errors
                })
                if verbose:
                    print(f"  ✗ {filename}: {len(errors)} errors")
                    for error in errors[:3]:
                        print(f"    - {error}")
            elif verbose:
                print(f"  ✓ {filename}")

        return all_valid

    def generate_manifest(self) -> Path:
        """Generate a manifest of all generated files."""
        manifest = {
            "version": "1.0.0",
            "compiled_at": self.results["timestamp"],
            "specs": {},
            "generated": self.results["generated"]
        }

        # Add spec versions
        for spec_file in self.specs_path.glob("*.json"):
            if spec_file.name != "manifest.json":
                with open(spec_file) as f:
                    data = json.load(f)
                    manifest["specs"][spec_file.stem] = {
                        "version": data.get("version", "unknown"),
                        "file": str(spec_file)
                    }

        manifest_path = self.src_path / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return manifest_path

    def clean(self, verbose: bool = True):
        """Clean generated files."""
        patterns = [
            self.src_path / "domain" / "models" / "*.py",
            self.src_path / "app" / "api" / "generated" / "*.py",
            self.src_path / "components" / "workbenches" / "*.tsx",
            self.src_path / "types" / "*.ts",
            self.src_path / "data" / "graph.json",
        ]

        cleaned = 0
        for pattern in patterns:
            for filepath in pattern.parent.glob(pattern.name):
                if filepath.is_file():
                    filepath.unlink()
                    cleaned += 1

        if verbose:
            print(f"Cleaned {cleaned} generated files")


def compile_specs(validate: bool = True, verbose: bool = True) -> dict:
    """Convenience function to compile all specs."""
    compiler = SpecCompiler()

    if validate:
        if not compiler.validate_specs(verbose):
            if verbose:
                print("\nValidation failed. Fix errors before compiling.")
            return compiler.results

    return compiler.compile_all(verbose)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Compile all specs")
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip spec validation"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean generated files before compiling"
    )
    parser.add_argument(
        "--manifest",
        action="store_true",
        help="Generate manifest file"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode"
    )

    args = parser.parse_args()
    verbose = not args.quiet

    compiler = SpecCompiler()

    if args.clean:
        compiler.clean(verbose)

    results = compile_specs(
        validate=not args.no_validate,
        verbose=verbose
    )

    if args.manifest:
        manifest_path = compiler.generate_manifest()
        if verbose:
            print(f"Generated manifest: {manifest_path}")

    # Exit with error code if there were errors
    if results["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
