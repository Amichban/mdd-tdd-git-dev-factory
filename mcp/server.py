#!/usr/bin/env python3
"""
MCP (Model Context Protocol) server for Dev Platform.

Exposes platform capabilities as tools for Claude Code.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.graph_builder import get_graph_builder
from services.signal_emitter import get_signal_emitter
from services.schema_validator import get_validator


class MCPServer:
    """MCP server exposing platform tools."""

    def __init__(self):
        self.tools = {
            "get_graph": self.get_graph,
            "get_node": self.get_node,
            "get_lineage": self.get_lineage,
            "search_nodes": self.search_nodes,
            "emit_signal": self.emit_signal,
            "validate_spec": self.validate_spec,
            "list_entities": self.list_entities,
            "list_workflows": self.list_workflows,
        }

    def handle_request(self, request: dict) -> dict:
        """Handle an MCP request."""
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return self._initialize(params)
        elif method == "tools/list":
            return self._list_tools()
        elif method == "tools/call":
            return self._call_tool(params)
        else:
            return {"error": f"Unknown method: {method}"}

    def _initialize(self, params: dict) -> dict:
        """Initialize the MCP connection."""
        return {
            "protocolVersion": "0.1.0",
            "serverInfo": {
                "name": "devplatform-mcp",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {}
            }
        }

    def _list_tools(self) -> dict:
        """List available tools."""
        return {
            "tools": [
                {
                    "name": "get_graph",
                    "description": "Get the complete business graph with all nodes and edges",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "get_node",
                    "description": "Get a specific node by ID",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "node_id": {
                                "type": "string",
                                "description": "The node ID to retrieve"
                            }
                        },
                        "required": ["node_id"]
                    }
                },
                {
                    "name": "get_lineage",
                    "description": "Get upstream or downstream lineage for a node",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "node_id": {
                                "type": "string",
                                "description": "The node ID to get lineage for"
                            },
                            "direction": {
                                "type": "string",
                                "enum": ["upstream", "downstream"],
                                "description": "Direction of lineage"
                            }
                        },
                        "required": ["node_id"]
                    }
                },
                {
                    "name": "search_nodes",
                    "description": "Search for nodes by query string",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "emit_signal",
                    "description": "Emit a signal event",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["status_change", "decision", "alert"],
                                "description": "Signal type"
                            },
                            "node_ref": {
                                "type": "string",
                                "description": "Reference to the node"
                            },
                            "payload": {
                                "type": "object",
                                "description": "Signal payload"
                            }
                        },
                        "required": ["type", "node_ref", "payload"]
                    }
                },
                {
                    "name": "validate_spec",
                    "description": "Validate a spec against its schema",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "spec_type": {
                                "type": "string",
                                "description": "Type of spec (entity, workflow, etc.)"
                            },
                            "data": {
                                "type": "object",
                                "description": "The spec data to validate"
                            }
                        },
                        "required": ["spec_type", "data"]
                    }
                },
                {
                    "name": "list_entities",
                    "description": "List all entities in the platform",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "list_workflows",
                    "description": "List all workflows in the platform",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }

    def _call_tool(self, params: dict) -> dict:
        """Call a tool with parameters."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self.tools:
            return {
                "error": f"Unknown tool: {tool_name}"
            }

        try:
            result = self.tools[tool_name](**arguments)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        except Exception as e:
            return {
                "error": str(e)
            }

    # Tool implementations
    def get_graph(self) -> dict:
        """Get the complete business graph."""
        builder = get_graph_builder()
        return builder.get_graph()

    def get_node(self, node_id: str) -> dict:
        """Get a specific node."""
        builder = get_graph_builder()
        node = builder.get_node(node_id)
        if node is None:
            return {"error": f"Node not found: {node_id}"}
        return node

    def get_lineage(self, node_id: str, direction: str = "upstream") -> dict:
        """Get lineage for a node."""
        builder = get_graph_builder()
        lineage = builder.get_lineage(node_id, direction)
        return {"node_id": node_id, "direction": direction, "lineage": lineage}

    def search_nodes(self, query: str) -> dict:
        """Search for nodes."""
        builder = get_graph_builder()
        results = builder.search_nodes(query)
        return {"query": query, "results": results}

    def emit_signal(self, type: str, node_ref: str, payload: dict) -> dict:
        """Emit a signal event."""
        emitter = get_signal_emitter()

        if type == "status_change":
            signal = emitter.emit_status_change(
                node_ref=node_ref,
                previous_status=payload.get("previous_status", "unknown"),
                new_status=payload.get("new_status", "unknown"),
                correlation_id=payload.get("correlation_id")
            )
        elif type == "decision":
            signal = emitter.emit_decision(
                node_ref=node_ref,
                condition=payload.get("condition", ""),
                reason=payload.get("reason", ""),
                impact=payload.get("impact", []),
                correlation_id=payload.get("correlation_id")
            )
        elif type == "alert":
            signal = emitter.emit_alert(
                node_ref=node_ref,
                severity=payload.get("severity", "info"),
                summary=payload.get("summary", ""),
                detail=payload.get("detail"),
                correlation_id=payload.get("correlation_id")
            )
        else:
            return {"error": f"Unknown signal type: {type}"}

        return {"success": True, "signal": signal}

    def validate_spec(self, spec_type: str, data: dict) -> dict:
        """Validate a spec."""
        validator = get_validator()
        is_valid, errors = validator.validate(data, spec_type)
        return {
            "valid": is_valid,
            "errors": errors
        }

    def list_entities(self) -> dict:
        """List all entities."""
        specs_path = Path(__file__).parent.parent / "specs" / "entities.json"
        if not specs_path.exists():
            return {"entities": []}

        with open(specs_path) as f:
            data = json.load(f)

        entities = []
        for entity in data.get("entities", []):
            entities.append({
                "name": entity.get("name"),
                "description": entity.get("description"),
                "layer": entity.get("layer")
            })

        return {"entities": entities}

    def list_workflows(self) -> dict:
        """List all workflows."""
        specs_path = Path(__file__).parent.parent / "specs" / "workflows.json"
        if not specs_path.exists():
            return {"workflows": []}

        with open(specs_path) as f:
            data = json.load(f)

        workflows = []
        for wf in data.get("workflows", []):
            workflows.append({
                "id": wf.get("id"),
                "name": wf.get("name"),
                "description": wf.get("description")
            })

        return {"workflows": workflows}


def run_server():
    """Run the MCP server using stdio transport."""
    server = MCPServer()

    # Read from stdin, write to stdout
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = server.handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON"}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)


if __name__ == "__main__":
    run_server()
