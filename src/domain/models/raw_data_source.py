"""
RawDataSource Model

AUTO-GENERATED from specs/entities.json
DO NOT EDIT MANUALLY - changes will be overwritten

Generated: 2024-01-01T00:00:00Z
Source: specs/entities.json#RawDataSource
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Enums
class SourceType(str, Enum):
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    WEBHOOK = "webhook"


class SyncStatus(str, Enum):
    PENDING = "pending"
    SYNCING = "syncing"
    SUCCESS = "success"
    FAILED = "failed"


# SQLAlchemy Model
class RawDataSourceDB(Base):
    """Database model for RawDataSource."""

    __tablename__ = "raw_data_sources"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, unique=True)
    source_type = Column(String(20), nullable=False)
    connection_string = Column(String, nullable=False)  # Sensitive - encrypt at rest
    schema_definition = Column(JSON, nullable=True)
    refresh_interval = Column(Integer, nullable=True, default=3600)
    is_active = Column(Boolean, nullable=False, default=True)
    last_sync_at = Column(DateTime, nullable=True)
    sync_status = Column(String(20), nullable=False, default="pending")
    error_message = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_raw_data_sources_name", "name", unique=True),
        Index("ix_raw_data_sources_type_active", "source_type", "is_active"),
        Index("ix_raw_data_sources_status", "sync_status"),
    )


# Pydantic Schemas
class RawDataSourceBase(BaseModel):
    """Base schema with common fields."""

    name: str = Field(..., max_length=100, description="Human-readable name for the data source")
    source_type: SourceType = Field(..., description="Type of data source")
    connection_string: str = Field(..., description="Connection string or URL (encrypted at rest)")
    schema_definition: Optional[dict[str, Any]] = Field(None, description="JSON schema of the expected data format")
    refresh_interval: Optional[int] = Field(3600, ge=60, description="How often to pull data (seconds)")
    is_active: bool = Field(True, description="Whether the source is currently active")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional configuration options")


class RawDataSourceCreate(RawDataSourceBase):
    """Schema for creating a new RawDataSource."""
    pass


class RawDataSourceUpdate(BaseModel):
    """Schema for updating an existing RawDataSource."""

    name: Optional[str] = Field(None, max_length=100)
    source_type: Optional[SourceType] = None
    connection_string: Optional[str] = None
    schema_definition: Optional[dict[str, Any]] = None
    refresh_interval: Optional[int] = Field(None, ge=60)
    is_active: Optional[bool] = None
    metadata: Optional[dict[str, Any]] = None


class RawDataSourceRead(RawDataSourceBase):
    """Schema for reading a RawDataSource."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    last_sync_at: Optional[datetime] = None
    sync_status: SyncStatus = SyncStatus.PENDING
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RawDataSourceList(BaseModel):
    """Schema for listing RawDataSources with pagination."""

    items: list[RawDataSourceRead]
    total: int
    page: int
    page_size: int
    pages: int
