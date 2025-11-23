"""Entity routers."""

from fastapi import APIRouter

from .raw_data_source import router as raw_data_source_router
from .market_data_source import router as market_data_source_router

router = APIRouter()

router.include_router(raw_data_source_router)
router.include_router(market_data_source_router)
