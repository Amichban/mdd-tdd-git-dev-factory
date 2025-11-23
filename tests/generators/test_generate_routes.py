"""Tests for generate_routes.py"""

import pytest
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generators.generate_routes import (
    generate_route_code,
    generate_routes,
)


class TestGenerateRouteCode:
    def test_generates_all_endpoints(self):
        entity = {
            "name": "TestEntity",
            "api": {
                "endpoints": ["list", "get", "create", "update", "delete"]
            }
        }

        code = generate_route_code(entity)

        assert "router = APIRouter" in code
        assert "@router.get(\"/\"" in code
        assert "@router.get(\"/{id}\"" in code
        assert "@router.post(\"/\"" in code
        assert "@router.patch(\"/{id}\"" in code
        assert "@router.delete(\"/{id}\"" in code

    def test_generates_only_specified_endpoints(self):
        entity = {
            "name": "ReadOnlyEntity",
            "api": {
                "endpoints": ["list", "get"]
            }
        }

        code = generate_route_code(entity)

        assert "@router.get(\"/\"" in code
        assert "@router.get(\"/{id}\"" in code
        assert "@router.post" not in code
        assert "@router.patch" not in code
        assert "@router.delete" not in code

    def test_uses_correct_model_imports(self):
        entity = {
            "name": "DataSource",
            "api": {
                "endpoints": ["create"]
            }
        }

        code = generate_route_code(entity)

        assert "from src.domain.models.datasource import DataSource" in code
        assert "DataSourceCreate" in code

    def test_generates_correct_route_prefix(self):
        entity = {
            "name": "RawDataSource",
            "api": {
                "endpoints": ["list"]
            }
        }

        code = generate_route_code(entity)

        assert 'prefix="/rawdatasources"' in code
        assert 'tags=["RawDataSource"]' in code


class TestGenerateRoutes:
    def test_generates_route_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            specs = {
                "entities": {
                    "entities": [
                        {
                            "name": "TestEntity",
                            "api": {
                                "endpoints": ["list", "get"]
                            }
                        }
                    ]
                }
            }

            generated = generate_routes(specs, output_dir)

            assert len(generated) == 2  # route file + __init__.py

            routes_dir = output_dir / "app" / "api" / "generated"
            assert routes_dir.exists()
            assert (routes_dir / "testentity.py").exists()
            assert (routes_dir / "__init__.py").exists()

    def test_generates_init_with_router_aggregation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            specs = {
                "entities": {
                    "entities": [
                        {"name": "Entity1", "api": {"endpoints": ["list"]}},
                        {"name": "Entity2", "api": {"endpoints": ["list"]}}
                    ]
                }
            }

            generate_routes(specs, output_dir)

            init_path = output_dir / "app" / "api" / "generated" / "__init__.py"
            content = init_path.read_text()

            assert "api_router = APIRouter()" in content
            assert "entity1_router" in content
            assert "entity2_router" in content
            assert "include_router" in content

    def test_handles_empty_entities(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            specs = {"entities": {"entities": []}}

            generated = generate_routes(specs, output_dir)

            assert len(generated) == 1  # just __init__.py
