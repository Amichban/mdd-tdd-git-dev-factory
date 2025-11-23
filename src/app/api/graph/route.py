"""
Graph API endpoints.
GET /api/graph - Fetch the business model graph.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from services.graph_builder import get_graph_builder

router = APIRouter(prefix="/graph", tags=["Graph"])


@router.get("/")
async def get_graph():
    """Get the full business graph."""
    builder = get_graph_builder()
    return builder.get_graph()


@router.get("/node/{node_id}")
async def get_node(node_id: str):
    """Get a specific node by ID."""
    builder = get_graph_builder()
    node = builder.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")
    return node


@router.get("/node/{node_id}/edges")
async def get_node_edges(node_id: str):
    """Get all edges connected to a node."""
    builder = get_graph_builder()
    return builder.get_edges_for_node(node_id)


@router.get("/node/{node_id}/lineage")
async def get_node_lineage(
    node_id: str,
    direction: str = Query("upstream", enum=["upstream", "downstream"])
):
    """Get lineage (upstream or downstream) for a node."""
    builder = get_graph_builder()
    return {
        "node_id": node_id,
        "direction": direction,
        "lineage": builder.get_lineage(node_id, direction)
    }


@router.get("/nodes")
async def list_nodes(
    node_type: Optional[str] = None,
    search: Optional[str] = None
):
    """List nodes with optional filtering."""
    builder = get_graph_builder()

    if search:
        return builder.search_nodes(search)
    elif node_type:
        return builder.get_nodes_by_type(node_type)
    else:
        return builder.get_graph()["nodes"]


@router.get("/stats")
async def get_graph_stats():
    """Get graph statistics."""
    builder = get_graph_builder()
    return builder.get_stats()
