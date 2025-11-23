"""Tests for generate_models.py"""

import pytest
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generators.generate_models import (
    snake_to_pascal,
    generate_field_type,
    generate_field_definition,
    generate_model,
    generate_all_models,
    load_entities,
)


class TestSnakeToPascal:
    def test_simple_conversion(self):
        assert snake_to_pascal("raw_data_source") == "RawDataSource"
        assert snake_to_pascal("user") == "User"
        assert snake_to_pascal("ml_model") == "MlModel"

    def test_single_word(self):
        assert snake_to_pascal("entity") == "Entity"

    def test_multiple_underscores(self):
        assert snake_to_pascal("my_long_entity_name") == "MyLongEntityName"


class TestGenerateFieldType:
    def test_basic_types(self):
        assert generate_field_type({"type": "string", "required": True}) == "str"
        assert generate_field_type({"type": "integer", "required": True}) == "int"
        assert generate_field_type({"type": "boolean", "required": True}) == "bool"
        assert generate_field_type({"type": "number", "required": True}) == "float"

    def test_optional_fields(self):
        assert generate_field_type({"type": "string", "required": False}) == "str | None"
        assert generate_field_type({"type": "integer"}) == "int | None"

    def test_optional_with_default(self):
        result = generate_field_type({"type": "string", "required": False, "default": "test"})
        assert result == "str"

    def test_enum_type(self):
        result = generate_field_type({
            "type": "enum",
            "values": ["pending", "active", "completed"],
            "required": True
        })
        assert 'Literal["pending", "active", "completed"]' == result

    def test_array_type(self):
        result = generate_field_type({
            "type": "array",
            "itemType": "string",
            "required": True
        })
        assert result == "list[str]"


class TestGenerateFieldDefinition:
    def test_simple_field(self):
        result = generate_field_definition({
            "id": "name",
            "type": "string",
            "required": True
        })
        assert "name: str" in result

    def test_field_with_description(self):
        result = generate_field_definition({
            "id": "title",
            "type": "string",
            "required": True,
            "description": "The title"
        })
        assert "title: str" in result
        assert 'description="The title"' in result

    def test_field_with_default(self):
        result = generate_field_definition({
            "id": "status",
            "type": "string",
            "required": False,
            "default": "pending"
        })
        assert 'default="pending"' in result

    def test_optional_field_without_default(self):
        result = generate_field_definition({
            "id": "notes",
            "type": "string",
            "required": False
        })
        assert "default=None" in result


class TestGenerateModel:
    def test_basic_model(self):
        entity = {
            "name": "TestEntity",
            "description": "A test entity",
            "properties": [
                {"id": "name", "type": "string", "required": True},
                {"id": "count", "type": "integer", "required": False}
            ]
        }
        result = generate_model(entity)
        assert "class TestEntity(BaseModel):" in result
        assert "A test entity" in result
        assert "name: str" in result
        assert "count: int | None" in result

    def test_model_with_datetime(self):
        entity = {
            "name": "TimestampEntity",
            "description": "Entity with timestamps",
            "properties": [
                {"id": "created_at", "type": "datetime", "required": True}
            ]
        }
        result = generate_model(entity)
        assert "from datetime import datetime" in result
        assert "created_at: datetime" in result


class TestGenerateAllModels:
    def test_generates_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            specs_path = Path(tmpdir) / "specs"
            output_path = Path(tmpdir) / "output"
            specs_path.mkdir()

            entities_data = {
                "version": "1.0.0",
                "entities": [
                    {
                        "id": "test_entity",
                        "name": "TestEntity",
                        "description": "Test entity",
                        "properties": [
                            {"id": "name", "type": "string", "required": True}
                        ]
                    }
                ]
            }

            with open(specs_path / "entities.json", "w") as f:
                json.dump(entities_data, f)

            generated = generate_all_models(specs_path, output_path)

            assert len(generated) == 2  # entity file + __init__.py
            assert output_path.exists()
            assert (output_path / "__init__.py").exists()
            assert (output_path / "test_entity.py").exists()


class TestLoadEntities:
    def test_loads_valid_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            specs_path = Path(tmpdir)
            entities_data = {"version": "1.0.0", "entities": []}

            with open(specs_path / "entities.json", "w") as f:
                json.dump(entities_data, f)

            result = load_entities(specs_path)
            assert result["version"] == "1.0.0"
            assert result["entities"] == []

    def test_raises_on_missing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            specs_path = Path(tmpdir)
            with pytest.raises(FileNotFoundError):
                load_entities(specs_path)
