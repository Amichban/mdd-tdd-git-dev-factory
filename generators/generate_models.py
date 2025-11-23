#!/usr/bin/env python3
"""
Generate Pydantic models from specs/entities.json

This generator reads entity definitions and produces:
- Pydantic model classes with typed fields
- Validation constraints
- Relationship references
- Action method stubs
"""

import json
from pathlib import Path
from datetime import datetime

# Type mapping from JSON spec to Python/Pydantic
TYPE_MAP = {
    "string": "str",
    "number": "float",
    "integer": "int",
    "boolean": "bool",
    "datetime": "datetime",
    "date": "date",
    "enum": "Literal",
    "array": "list",
    "object": "dict",
}


def load_entities(specs_path: Path) -> dict:
    """Load entities from JSON spec file."""
    entities_file = specs_path / "entities.json"
    with open(entities_file) as f:
        return json.load(f)


def snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def generate_field_type(prop: dict) -> str:
    """Generate Python type annotation for a property."""
    prop_type = prop["type"]
    base_type = TYPE_MAP.get(prop_type, "Any")

    if prop_type == "enum":
        values = prop.get("values", [])
        if values:
            quoted = [f'"{v}"' for v in values]
            base_type = f"Literal[{', '.join(quoted)}]"
    elif prop_type == "array":
        item_type = prop.get("itemType", "Any")
        base_type = f"list[{TYPE_MAP.get(item_type, 'Any')}]"

    # Handle optional fields
    if not prop.get("required", False):
        if "default" in prop:
            return base_type
        return f"{base_type} | None"

    return base_type


def generate_field_definition(prop: dict) -> str:
    """Generate Pydantic Field definition for a property."""
    field_type = generate_field_type(prop)
    field_args = []

    # Description
    if "description" in prop:
        field_args.append(f'description="{prop["description"]}"')

    # Constraints
    constraints = prop.get("constraints", {})
    if "min" in constraints:
        field_args.append(f"ge={constraints['min']}")
    if "max" in constraints:
        field_args.append(f"le={constraints['max']}")
    if "minLength" in constraints:
        field_args.append(f"min_length={constraints['minLength']}")
    if "maxLength" in constraints:
        field_args.append(f"max_length={constraints['maxLength']}")
    if "pattern" in constraints:
        field_args.append(f'pattern=r"{constraints["pattern"]}"')

    # Default value
    if "default" in prop:
        default = prop["default"]
        if isinstance(default, str):
            field_args.append(f'default="{default}"')
        else:
            field_args.append(f"default={default}")
    elif not prop.get("required", False):
        field_args.append("default=None")

    # Build field definition
    if field_args:
        return f"{prop['id']}: {field_type} = Field({', '.join(field_args)})"
    else:
        return f"{prop['id']}: {field_type}"


def generate_relationship_field(rel: dict) -> str:
    """Generate field for a relationship."""
    target = snake_to_pascal(rel["targetEntity"])
    rel_type = rel["type"]

    if rel_type in ["many-to-one", "one-to-one"]:
        # Reference by ID
        field_type = "str"
        field_name = f"{rel['id']}_id"
    else:
        # List of IDs
        field_type = "list[str]"
        field_name = f"{rel['id']}_ids"

    required = rel.get("required", False)
    if not required:
        field_type = f"{field_type} | None"

    desc = rel.get("description", f"Reference to {target}")

    if required:
        return f'{field_name}: {field_type} = Field(description="{desc}")'
    else:
        return f'{field_name}: {field_type} = Field(default=None, description="{desc}")'


def generate_action_method(action: dict, entity_name: str) -> str:
    """Generate method stub for an action."""
    params = action.get("parameters", [])
    param_strs = ["self"]

    for param in params:
        param_type = TYPE_MAP.get(param.get("type", "string"), "Any")
        param_strs.append(f"{param['id']}: {param_type}")

    method_sig = f"def {action['id']}({', '.join(param_strs)}):"

    # Build docstring
    docstring = f'"""{action["description"]}'

    if action.get("preconditions"):
        docstring += "\n\n        Preconditions:\n"
        for pre in action["preconditions"]:
            docstring += f"        - {pre}\n"

    if action.get("postconditions"):
        docstring += "\n        Postconditions:\n"
        for post in action["postconditions"]:
            docstring += f"        - {post}\n"

    docstring += '"""'

    return f"""    {method_sig}
        {docstring}
        # TODO: Implement action logic
        raise NotImplementedError("{action['id']} not implemented")
"""


def generate_model(entity: dict) -> str:
    """Generate complete Pydantic model for an entity."""
    class_name = entity["name"]
    description = entity["description"]

    # Collect imports needed
    imports = set()
    imports.add("from pydantic import BaseModel, Field")

    # Check if we need specific imports
    for prop in entity.get("properties", []):
        if prop["type"] == "datetime":
            imports.add("from datetime import datetime")
        elif prop["type"] == "date":
            imports.add("from datetime import date")
        elif prop["type"] == "enum":
            imports.add("from typing import Literal")

    # Build class
    lines = [
        f'class {class_name}(BaseModel):',
        f'    """{description}"""',
        '',
    ]

    # Properties
    for prop in entity.get("properties", []):
        lines.append(f"    {generate_field_definition(prop)}")

    # Relationships
    if entity.get("relationships"):
        lines.append("")
        lines.append("    # Relationships")
        for rel in entity["relationships"]:
            lines.append(f"    {generate_relationship_field(rel)}")

    # Actions
    if entity.get("actions"):
        lines.append("")
        lines.append("    # Actions")
        for action in entity["actions"]:
            lines.append(generate_action_method(action, class_name))

    return "\n".join(sorted(imports)) + "\n\n" + "\n".join(lines)


def generate_all_models(specs_path: Path, output_path: Path) -> list[str]:
    """Generate all models from entities.json."""
    data = load_entities(specs_path)
    generated_files = []

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate __init__.py
    init_imports = []

    for entity in data.get("entities", []):
        entity_id = entity["id"]
        class_name = entity["name"]

        # Generate model file
        model_code = generate_model(entity)
        model_file = output_path / f"{entity_id}.py"

        with open(model_file, "w") as f:
            f.write(f'"""\nGenerated from specs/entities.json\nDo not edit directly - changes will be overwritten\nGenerated at: {datetime.now().isoformat()}\n"""\n\n')
            f.write(model_code)

        generated_files.append(str(model_file))
        init_imports.append(f"from .{entity_id} import {class_name}")

    # Write __init__.py
    init_file = output_path / "__init__.py"
    with open(init_file, "w") as f:
        f.write('"""Generated models from specs/entities.json"""\n\n')
        f.write("\n".join(init_imports))
        if init_imports:
            f.write("\n\n__all__ = [\n")
            for entity in data.get("entities", []):
                f.write(f'    "{entity["name"]}",\n')
            f.write("]\n")

    generated_files.append(str(init_file))
    return generated_files


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    specs_path = project_root / "specs"
    output_path = project_root / "src" / "domain" / "models"

    print(f"Generating models from {specs_path}/entities.json")

    generated = generate_all_models(specs_path, output_path)

    if generated:
        print(f"Generated {len(generated)} files:")
        for f in generated:
            print(f"  - {f}")
    else:
        print("No entities found in specs/entities.json")


if __name__ == "__main__":
    main()
