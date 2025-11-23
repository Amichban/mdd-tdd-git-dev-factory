"""
FastAPI Application Entry Point

This is the main entry point for the backend API.
All routes are auto-generated from specs.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create FastAPI app
app = FastAPI(
    title="Development Platform API",
    description="Model-driven development platform with full observability",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

# Add production origins from environment
if os.getenv("FRONTEND_URL"):
    origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "env": os.getenv("ENV", "development"),
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Development Platform API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


# Import and include generated routers
# These are auto-generated from specs/entities.json
try:
    from src.app.api.generated import routers
    for router in routers:
        app.include_router(router)
except ImportError:
    # Generated routers not yet created
    pass


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Connect to database
    # Initialize event bus
    # Load configurations
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    # Close database connections
    # Flush event bus
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENV") == "development",
    )
