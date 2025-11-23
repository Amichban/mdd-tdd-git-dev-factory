"""
Tests for MarketDataSource entity
Generated from specs/entities.json
Generated at: 2025-11-23T19:24:59.550888
"""

import pytest
from pydantic import ValidationError

from domain.models.market_data_source import MarketDataSource


class TestMarketDataSource:
    """Market data provider configuration for financial data ingestion"""
