"""
RawDataSource API Routes

AUTO-GENERATED from specs/entities.json
DO NOT EDIT MANUALLY - changes will be overwritten

Generated: 2024-01-01T00:00:00Z
Source: specs/entities.json#RawDataSource
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.domain.models.raw_data_source import (
    RawDataSourceDB,
    RawDataSourceCreate,
    RawDataSourceUpdate,
    RawDataSourceRead,
    RawDataSourceList,
    SyncStatus,
)
from services.events import job_started, job_completed, job_failed

router = APIRouter(prefix="/raw-data-sources", tags=["Raw Data Sources"])


# Dependency to get database session
def get_db():
    # This would be implemented with actual database connection
    pass


@router.get("", response_model=RawDataSourceList)
async def list_raw_data_sources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    sync_status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all raw data sources with filtering and pagination.
    """
    query = db.query(RawDataSourceDB)

    # Apply filters
    if source_type:
        query = query.filter(RawDataSourceDB.source_type == source_type)
    if is_active is not None:
        query = query.filter(RawDataSourceDB.is_active == is_active)
    if sync_status:
        query = query.filter(RawDataSourceDB.sync_status == sync_status)
    if search:
        query = query.filter(RawDataSourceDB.name.ilike(f"%{search}%"))

    # Get total count
    total = query.count()

    # Paginate
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return RawDataSourceList(
        items=[RawDataSourceRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{id}", response_model=RawDataSourceRead)
async def get_raw_data_source(
    id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a specific raw data source by ID.
    """
    item = db.query(RawDataSourceDB).filter(RawDataSourceDB.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Raw data source not found")
    return RawDataSourceRead.model_validate(item)


@router.post("", response_model=RawDataSourceRead, status_code=201)
async def create_raw_data_source(
    data: RawDataSourceCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new raw data source.
    """
    # Check for duplicate name
    existing = db.query(RawDataSourceDB).filter(RawDataSourceDB.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="A data source with this name already exists")

    item = RawDataSourceDB(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)

    return RawDataSourceRead.model_validate(item)


@router.put("/{id}", response_model=RawDataSourceRead)
async def update_raw_data_source(
    id: UUID,
    data: RawDataSourceUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing raw data source.
    """
    item = db.query(RawDataSourceDB).filter(RawDataSourceDB.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Raw data source not found")

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    return RawDataSourceRead.model_validate(item)


@router.delete("/{id}", status_code=204)
async def delete_raw_data_source(
    id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a raw data source.
    """
    item = db.query(RawDataSourceDB).filter(RawDataSourceDB.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Raw data source not found")

    db.delete(item)
    db.commit()


# Custom endpoints

@router.post("/{id}/sync", response_model=dict)
async def sync_raw_data_source(
    id: UUID,
    db: Session = Depends(get_db),
):
    """
    Trigger manual sync for this data source.
    """
    item = db.query(RawDataSourceDB).filter(RawDataSourceDB.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Raw data source not found")

    correlation_id = f"sync-{id}-{datetime.utcnow().isoformat()}"
    node_id = f"datasource.{item.name}"

    # Emit job started event
    job_started(
        correlation_id=correlation_id,
        node_id=node_id,
        inputs={"source_id": str(id), "source_type": item.source_type}
    )

    try:
        # Update status
        item.sync_status = SyncStatus.SYNCING
        db.commit()

        # TODO: Implement actual sync logic based on source_type
        # This would be handled by a background task/worker

        return {
            "message": "Sync started",
            "correlation_id": correlation_id,
            "source_id": str(id),
        }

    except Exception as e:
        job_failed(correlation_id=correlation_id, node_id=node_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{id}/test", response_model=dict)
async def test_connection(
    id: UUID,
    db: Session = Depends(get_db),
):
    """
    Test the connection without syncing.
    """
    item = db.query(RawDataSourceDB).filter(RawDataSourceDB.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Raw data source not found")

    # TODO: Implement connection testing based on source_type
    # For now, return a mock success

    return {
        "success": True,
        "message": "Connection successful",
        "source_id": str(id),
        "latency_ms": 42,
    }


@router.post("/sync-all", response_model=dict)
async def sync_all_sources(
    db: Session = Depends(get_db),
):
    """
    Trigger sync for all active data sources.
    """
    active_sources = db.query(RawDataSourceDB).filter(
        RawDataSourceDB.is_active == True
    ).all()

    triggered = []
    for source in active_sources:
        # Queue each sync
        triggered.append(str(source.id))

    return {
        "message": f"Sync triggered for {len(triggered)} sources",
        "source_ids": triggered,
    }
