#!/usr/bin/env python3
"""
Generate FastAPI routes from entity specs.
"""

from pathlib import Path


def generate_route_code(entity: dict) -> str:
    """Generate FastAPI route code for an entity."""
    name = entity['name']
    name_lower = name.lower()
    name_plural = f"{name_lower}s"

    # Get API config
    api_config = entity.get('api', {})
    endpoints = api_config.get('endpoints', ['list', 'get', 'create', 'update', 'delete'])

    code = f'''"""
Auto-generated FastAPI routes for {name}.
DO NOT EDIT - Generated from specs/entities.json
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.domain.models.{name_lower} import {name}, {name}Create, {name}Update
from services.database import get_db

router = APIRouter(prefix="/{name_plural}", tags=["{name}"])

'''

    # List endpoint
    if 'list' in endpoints:
        code += f'''
@router.get("/", response_model=list[{name}])
async def list_{name_plural}(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all {name_plural}."""
    items = db.query({name}).offset(skip).limit(limit).all()
    return items

'''

    # Get endpoint
    if 'get' in endpoints:
        code += f'''
@router.get("/{{id}}", response_model={name})
async def get_{name_lower}(id: UUID, db: Session = Depends(get_db)):
    """Get a {name_lower} by ID."""
    item = db.query({name}).filter({name}.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{name} not found")
    return item

'''

    # Create endpoint
    if 'create' in endpoints:
        code += f'''
@router.post("/", response_model={name}, status_code=201)
async def create_{name_lower}(
    data: {name}Create,
    db: Session = Depends(get_db)
):
    """Create a new {name_lower}."""
    item = {name}(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

'''

    # Update endpoint
    if 'update' in endpoints:
        code += f'''
@router.patch("/{{id}}", response_model={name})
async def update_{name_lower}(
    id: UUID,
    data: {name}Update,
    db: Session = Depends(get_db)
):
    """Update a {name_lower}."""
    item = db.query({name}).filter({name}.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{name} not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item

'''

    # Delete endpoint
    if 'delete' in endpoints:
        code += f'''
@router.delete("/{{id}}", status_code=204)
async def delete_{name_lower}(id: UUID, db: Session = Depends(get_db)):
    """Delete a {name_lower}."""
    item = db.query({name}).filter({name}.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{name} not found")

    db.delete(item)
    db.commit()
    return None
'''

    return code


def generate_routes(specs: dict, output_dir: Path) -> list[Path]:
    """Generate all route files from specs."""
    entities = specs.get('entities', {}).get('entities', [])
    routes_dir = output_dir / 'app' / 'api' / 'generated'
    routes_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []
    router_imports = []

    for entity in entities:
        name = entity['name']
        name_lower = name.lower()
        filename = f"{name_lower}.py"
        filepath = routes_dir / filename

        code = generate_route_code(entity)
        filepath.write_text(code)
        generated_files.append(filepath)
        router_imports.append((name_lower, f"{name_lower}s"))
        print(f"  ✓ {filepath}")

    # Generate __init__.py with router aggregation
    init_code = '''"""Auto-generated API routes."""

from fastapi import APIRouter

'''

    for name_lower, _ in router_imports:
        init_code += f"from .{name_lower} import router as {name_lower}_router\n"

    init_code += "\n\napi_router = APIRouter()\n\n"

    for name_lower, prefix in router_imports:
        init_code += f'api_router.include_router({name_lower}_router)\n'

    init_path = routes_dir / '__init__.py'
    init_path.write_text(init_code)
    generated_files.append(init_path)

    return generated_files
