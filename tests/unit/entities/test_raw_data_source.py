"""
Tests for RawDataSource entity
Generated from specs/entities.json
Generated at: 2025-11-23T19:24:59.550838
"""

import pytest
from pydantic import ValidationError

from domain.models.raw_data_source import RawDataSource


class TestRawDataSource:
    """External data source configuration for ingestion pipelines"""
