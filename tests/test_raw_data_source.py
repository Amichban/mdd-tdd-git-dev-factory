"""
RawDataSource Tests

AUTO-GENERATED from specs/entities.json
DO NOT EDIT MANUALLY - changes will be overwritten

Generated: 2024-01-01T00:00:00Z
Source: specs/entities.json#RawDataSource
"""

import pytest
from uuid import uuid4
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.api.main import app
from src.domain.models.raw_data_source import (
    RawDataSourceDB,
    RawDataSourceCreate,
    RawDataSourceUpdate,
    RawDataSourceRead,
    SourceType,
    SyncStatus,
    Base,
)


# Test database setup
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# Model Tests
class TestRawDataSourceModel:
    """Test Pydantic model validation."""

    def test_create_valid_source(self):
        """Test creating a valid data source."""
        data = RawDataSourceCreate(
            name="test_source",
            source_type=SourceType.DATABASE,
            connection_string="postgresql://localhost/test",
            refresh_interval=3600,
            is_active=True,
        )
        assert data.name == "test_source"
        assert data.source_type == SourceType.DATABASE
        assert data.refresh_interval == 3600

    def test_name_max_length(self):
        """Test name field max length validation."""
        with pytest.raises(ValueError):
            RawDataSourceCreate(
                name="x" * 101,  # Exceeds max_length of 100
                source_type=SourceType.API,
                connection_string="https://api.example.com",
            )

    def test_refresh_interval_minimum(self):
        """Test refresh_interval minimum value validation."""
        with pytest.raises(ValueError):
            RawDataSourceCreate(
                name="test",
                source_type=SourceType.FILE,
                connection_string="/path/to/file",
                refresh_interval=30,  # Below minimum of 60
            )

    def test_invalid_source_type(self):
        """Test invalid source_type validation."""
        with pytest.raises(ValueError):
            RawDataSourceCreate(
                name="test",
                source_type="invalid_type",
                connection_string="test",
            )

    def test_optional_fields_default(self):
        """Test optional fields have correct defaults."""
        data = RawDataSourceCreate(
            name="test",
            source_type=SourceType.WEBHOOK,
            connection_string="https://webhook.example.com",
        )
        assert data.refresh_interval == 3600
        assert data.is_active is True
        assert data.schema_definition is None
        assert data.metadata is None


# API Tests
class TestRawDataSourceAPI:
    """Test API endpoints."""

    def test_list_empty(self, client):
        """Test listing when no sources exist."""
        response = client.get("/raw-data-sources")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_create_source(self, client):
        """Test creating a new data source."""
        payload = {
            "name": "production_db",
            "source_type": "database",
            "connection_string": "postgresql://prod:5432/main",
            "refresh_interval": 1800,
            "is_active": True,
        }
        response = client.post("/raw-data-sources", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "production_db"
        assert data["source_type"] == "database"
        assert data["sync_status"] == "pending"
        assert "id" in data

    def test_create_duplicate_name(self, client):
        """Test creating source with duplicate name fails."""
        payload = {
            "name": "unique_source",
            "source_type": "api",
            "connection_string": "https://api.example.com",
        }
        # Create first
        client.post("/raw-data-sources", json=payload)
        # Try to create duplicate
        response = client.post("/raw-data-sources", json=payload)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_get_source(self, client):
        """Test getting a specific source."""
        # Create source first
        create_response = client.post("/raw-data-sources", json={
            "name": "test_source",
            "source_type": "file",
            "connection_string": "/data/input.csv",
        })
        source_id = create_response.json()["id"]

        # Get it
        response = client.get(f"/raw-data-sources/{source_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "test_source"

    def test_get_nonexistent(self, client):
        """Test getting nonexistent source returns 404."""
        fake_id = str(uuid4())
        response = client.get(f"/raw-data-sources/{fake_id}")
        assert response.status_code == 404

    def test_update_source(self, client):
        """Test updating a source."""
        # Create
        create_response = client.post("/raw-data-sources", json={
            "name": "old_name",
            "source_type": "stream",
            "connection_string": "kafka://localhost:9092",
        })
        source_id = create_response.json()["id"]

        # Update
        response = client.put(f"/raw-data-sources/{source_id}", json={
            "name": "new_name",
            "refresh_interval": 7200,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "new_name"
        assert data["refresh_interval"] == 7200
        # Unchanged fields stay the same
        assert data["source_type"] == "stream"

    def test_delete_source(self, client):
        """Test deleting a source."""
        # Create
        create_response = client.post("/raw-data-sources", json={
            "name": "to_delete",
            "source_type": "api",
            "connection_string": "https://delete.me",
        })
        source_id = create_response.json()["id"]

        # Delete
        response = client.delete(f"/raw-data-sources/{source_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/raw-data-sources/{source_id}")
        assert get_response.status_code == 404

    def test_filter_by_source_type(self, client):
        """Test filtering sources by type."""
        # Create sources of different types
        client.post("/raw-data-sources", json={
            "name": "db1",
            "source_type": "database",
            "connection_string": "pg://1",
        })
        client.post("/raw-data-sources", json={
            "name": "api1",
            "source_type": "api",
            "connection_string": "https://1",
        })

        # Filter
        response = client.get("/raw-data-sources?source_type=database")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "db1"

    def test_filter_by_active_status(self, client):
        """Test filtering by active status."""
        client.post("/raw-data-sources", json={
            "name": "active",
            "source_type": "file",
            "connection_string": "/a",
            "is_active": True,
        })
        client.post("/raw-data-sources", json={
            "name": "inactive",
            "source_type": "file",
            "connection_string": "/b",
            "is_active": False,
        })

        response = client.get("/raw-data-sources?is_active=true")
        assert response.json()["total"] == 1
        assert response.json()["items"][0]["name"] == "active"

    def test_search_by_name(self, client):
        """Test searching sources by name."""
        client.post("/raw-data-sources", json={
            "name": "production_database",
            "source_type": "database",
            "connection_string": "pg://prod",
        })
        client.post("/raw-data-sources", json={
            "name": "staging_api",
            "source_type": "api",
            "connection_string": "https://stage",
        })

        response = client.get("/raw-data-sources?search=prod")
        data = response.json()
        assert data["total"] == 1
        assert "production" in data["items"][0]["name"]

    def test_pagination(self, client):
        """Test pagination works correctly."""
        # Create 25 sources
        for i in range(25):
            client.post("/raw-data-sources", json={
                "name": f"source_{i:02d}",
                "source_type": "file",
                "connection_string": f"/path/{i}",
            })

        # Get first page
        response = client.get("/raw-data-sources?page=1&page_size=10")
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["pages"] == 3

        # Get second page
        response = client.get("/raw-data-sources?page=2&page_size=10")
        assert len(response.json()["items"]) == 10

        # Get last page
        response = client.get("/raw-data-sources?page=3&page_size=10")
        assert len(response.json()["items"]) == 5


# Custom Endpoint Tests
class TestCustomEndpoints:
    """Test custom endpoints (sync, test_connection)."""

    def test_sync_source(self, client):
        """Test triggering sync on a source."""
        create_response = client.post("/raw-data-sources", json={
            "name": "sync_test",
            "source_type": "database",
            "connection_string": "pg://test",
        })
        source_id = create_response.json()["id"]

        response = client.post(f"/raw-data-sources/{source_id}/sync")
        assert response.status_code == 200
        data = response.json()
        assert "correlation_id" in data
        assert data["source_id"] == source_id

    def test_test_connection(self, client):
        """Test connection testing endpoint."""
        create_response = client.post("/raw-data-sources", json={
            "name": "conn_test",
            "source_type": "api",
            "connection_string": "https://api.test",
        })
        source_id = create_response.json()["id"]

        response = client.post(f"/raw-data-sources/{source_id}/test")
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_sync_all(self, client):
        """Test syncing all active sources."""
        # Create mix of active/inactive
        client.post("/raw-data-sources", json={
            "name": "active1",
            "source_type": "file",
            "connection_string": "/1",
            "is_active": True,
        })
        client.post("/raw-data-sources", json={
            "name": "inactive1",
            "source_type": "file",
            "connection_string": "/2",
            "is_active": False,
        })

        response = client.post("/raw-data-sources/sync-all")
        assert response.status_code == 200
        # Only active source should be synced
        assert len(response.json()["source_ids"]) == 1
