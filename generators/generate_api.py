#!/usr/bin/env python3
"""
Generate FastAPI routes from specs/entities.json and specs/workflows.json

This generator produces:
- CRUD endpoints for each entity
- Action endpoints for entity actions
- Workflow transition endpoints
"""

import json
from pathlib import Path
from datetime import datetime


def load_entities(specs_path: Path) -> dict:
    """Load entities from JSON spec file."""
    with open(specs_path / "entities.json") as f:
        return json.load(f)


def load_workflows(specs_path: Path) -> dict:
    """Load workflows from JSON spec file."""
    with open(specs_path / "workflows.json") as f:
        return json.load(f)


def snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def generate_entity_router(entity: dict) -> str:
    """Generate FastAPI router for an entity."""
    entity_id = entity["id"]
    class_name = entity["name"]
    plural = entity_id + "s"  # Simple pluralization

    lines = [
        f'"""',
        f'API routes for {class_name}',
        f'Generated from specs/entities.json',
        f'Generated at: {datetime.now().isoformat()}',
        f'"""',
        '',
        'from fastapi import APIRouter, HTTPException, Depends',
        'from typing import List',
        '',
        f'from domain.models.{entity_id} import {class_name}',
        '# from services.database import get_db',
        '',
        f'router = APIRouter(prefix="/{plural}", tags=["{class_name}"])',
        '',
        '',
        '# CRUD Operations',
        '',
        f'@router.get("/", response_model=List[{class_name}])',
        f'async def list_{plural}(skip: int = 0, limit: int = 100):',
        f'    """List all {plural}."""',
        '    # TODO: Implement database query',
        f'    return []',
        '',
        '',
        f'@router.get("/{{id}}", response_model={class_name})',
        f'async def get_{entity_id}(id: str):',
        f'    """Get a {entity_id} by ID."""',
        '    # TODO: Implement database query',
        '    raise HTTPException(status_code=404, detail=f"{class_name} {id} not found")',
        '',
        '',
        f'@router.post("/", response_model={class_name}, status_code=201)',
        f'async def create_{entity_id}(item: {class_name}):',
        f'    """Create a new {entity_id}."""',
        '    # TODO: Implement database insert',
        '    return item',
        '',
        '',
        f'@router.put("/{{id}}", response_model={class_name})',
        f'async def update_{entity_id}(id: str, item: {class_name}):',
        f'    """Update an existing {entity_id}."""',
        '    # TODO: Implement database update',
        '    return item',
        '',
        '',
        f'@router.delete("/{{id}}", status_code=204)',
        f'async def delete_{entity_id}(id: str):',
        f'    """Delete a {entity_id}."""',
        '    # TODO: Implement database delete',
        '    pass',
        '',
    ]

    # Generate action endpoints
    actions = entity.get("actions", [])
    if actions:
        lines.append('')
        lines.append('# Action Endpoints')

    for action in actions:
        action_id = action["id"]
        action_name = action["name"]
        params = action.get("parameters", [])

        # Build parameter list
        if params:
            param_strs = []
            for param in params:
                param_type = param.get("type", "str")
                type_map = {"string": "str", "number": "float", "integer": "int", "boolean": "bool"}
                py_type = type_map.get(param_type, "str")
                param_strs.append(f'{param["id"]}: {py_type}')

            lines.append('')
            lines.append(f'@router.post("/{{id}}/{action_id}")')
            lines.append(f'async def {action_id}_{entity_id}(id: str, {", ".join(param_strs)}):')
        else:
            lines.append('')
            lines.append(f'@router.post("/{{id}}/{action_id}")')
            lines.append(f'async def {action_id}_{entity_id}(id: str):')

        lines.append(f'    """{action["description"]}"""')

        # Add precondition checks
        if action.get("preconditions"):
            lines.append('    # Check preconditions')
            for pre in action["preconditions"]:
                lines.append(f'    # - {pre}')

        lines.append('    # TODO: Implement action logic')

        # Add postcondition comments
        if action.get("postconditions"):
            lines.append('    # Apply postconditions')
            for post in action["postconditions"]:
                lines.append(f'    # - {post}')

        lines.append('    return {"status": "success"}')

    return "\n".join(lines)


def generate_workflow_router(workflow: dict) -> str:
    """Generate FastAPI router for workflow transitions."""
    workflow_id = workflow["id"]
    workflow_name = workflow["name"]
    route_name = workflow_id.replace("workflow_", "")

    lines = [
        f'"""',
        f'API routes for {workflow_name}',
        f'Generated from specs/workflows.json',
        f'Generated at: {datetime.now().isoformat()}',
        f'"""',
        '',
        'from fastapi import APIRouter, HTTPException',
        'from pydantic import BaseModel',
        'from typing import Optional',
        '',
        f'router = APIRouter(prefix="/workflows/{route_name}", tags=["{workflow_name}"])',
        '',
        '',
        '# State model',
        'class WorkflowState(BaseModel):',
        '    current_state: str',
        '    entity_id: str',
        '    history: list[dict] = []',
        '',
        '',
        '# Valid states',
        f'STATES = {[s["id"] for s in workflow.get("states", [])]}',
        '',
        '# Transition endpoints',
    ]

    # Generate transition endpoints
    for transition in workflow.get("transitions", []):
        trans_id = transition["id"]
        trans_name = transition["name"]
        from_state = transition["from"]
        to_state = transition["to"]

        lines.append('')
        lines.append(f'@router.post("/transitions/{trans_id}")')
        lines.append(f'async def {trans_id}(entity_id: str):')
        lines.append(f'    """')
        lines.append(f'    {trans_name}')
        lines.append(f'    From: {from_state} -> To: {to_state}')
        lines.append(f'    """')

        # Check conditions
        if transition.get("conditions"):
            lines.append('    # Check conditions')
            for cond in transition["conditions"]:
                lines.append(f'    # - {cond}')

        # Execute actions
        if transition.get("actions"):
            lines.append('    # Execute actions')
            for action in transition["actions"]:
                lines.append(f'    # - {action}')

        lines.append('')
        lines.append('    # TODO: Implement transition logic')
        lines.append(f'    return {{"from": "{from_state}", "to": "{to_state}", "entity_id": entity_id}}')

    # Add status endpoint
    lines.append('')
    lines.append('@router.get("/status/{entity_id}")')
    lines.append('async def get_status(entity_id: str):')
    lines.append(f'    """Get current workflow state for an entity."""')
    lines.append('    # TODO: Query current state')
    lines.append('    return {"entity_id": entity_id, "current_state": "unknown"}')

    return "\n".join(lines)


def generate_main_app() -> str:
    """Generate main FastAPI application."""
    return '''"""
Main FastAPI application
Generated from specs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Development Platform API",
    description="Auto-generated API from ontology specs",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
# from .entities import router as entities_router
# from .workflows import router as workflows_router
# app.include_router(entities_router)
# app.include_router(workflows_router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
'''


def generate_all_apis(specs_path: Path, output_path: Path) -> list[str]:
    """Generate all API routes from specs."""
    generated_files = []

    # Ensure output directories exist
    entities_path = output_path / "entities"
    workflows_path = output_path / "workflows"
    entities_path.mkdir(parents=True, exist_ok=True)
    workflows_path.mkdir(parents=True, exist_ok=True)

    # Generate entity routers
    entity_data = load_entities(specs_path)
    entity_imports = []

    for entity in entity_data.get("entities", []):
        router_code = generate_entity_router(entity)
        router_file = entities_path / f"{entity['id']}.py"

        with open(router_file, "w") as f:
            f.write(router_code)

        generated_files.append(str(router_file))
        entity_imports.append(f"from .{entity['id']} import router as {entity['id']}_router")

    # Generate entities __init__.py
    init_file = entities_path / "__init__.py"
    with open(init_file, "w") as f:
        f.write('"""Entity routers."""\n\n')
        f.write("from fastapi import APIRouter\n\n")
        f.write("\n".join(entity_imports))
        f.write("\n\nrouter = APIRouter()\n\n")
        for entity in entity_data.get("entities", []):
            f.write(f"router.include_router({entity['id']}_router)\n")
    generated_files.append(str(init_file))

    # Generate workflow routers
    workflow_data = load_workflows(specs_path)
    workflow_imports = []

    for workflow in workflow_data.get("workflows", []):
        router_code = generate_workflow_router(workflow)
        route_name = workflow["id"].replace("workflow_", "")
        router_file = workflows_path / f"{route_name}.py"

        with open(router_file, "w") as f:
            f.write(router_code)

        generated_files.append(str(router_file))
        workflow_imports.append(f"from .{route_name} import router as {route_name}_router")

    # Generate workflows __init__.py
    init_file = workflows_path / "__init__.py"
    with open(init_file, "w") as f:
        f.write('"""Workflow routers."""\n\n')
        f.write("from fastapi import APIRouter\n\n")
        f.write("\n".join(workflow_imports))
        f.write("\n\nrouter = APIRouter()\n\n")
        for workflow in workflow_data.get("workflows", []):
            route_name = workflow["id"].replace("workflow_", "")
            f.write(f"router.include_router({route_name}_router)\n")
    generated_files.append(str(init_file))

    # Generate main app
    main_file = output_path / "main.py"
    with open(main_file, "w") as f:
        f.write(generate_main_app())
    generated_files.append(str(main_file))

    return generated_files


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    specs_path = project_root / "specs"
    output_path = project_root / "src" / "app" / "api"

    print(f"Generating API routes from {specs_path}")

    generated = generate_all_apis(specs_path, output_path)

    if generated:
        print(f"Generated {len(generated)} files:")
        for f in generated:
            print(f"  - {f}")
    else:
        print("No entities or workflows found in specs")


if __name__ == "__main__":
    main()
