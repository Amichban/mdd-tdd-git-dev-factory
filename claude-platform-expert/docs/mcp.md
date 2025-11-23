# Model Context Protocol (MCP)

## What is MCP?
MCP is an open-source standard that enables AI systems like Claude Code to integrate with external tools, databases, and APIs. It acts as a bridge between Claude and hundreds of third-party services.

## How MCP Works
MCP operates through servers that expose capabilities to Claude Code:
- **Remote HTTP services** for cloud-based integrations
- **Local processes** for system-level access
- **SSE (Server-Sent Events)** for real-time connections

## Practical Applications
- Extract data from issue tracking systems and create pull requests
- Monitor errors across production environments
- Query databases with natural language
- Automate workflows across multiple platforms

## Installation & Configuration

### Add HTTP Server (recommended for remote services)
```bash
claude mcp add --transport http [name] [url]
```

### Add Local Stdio Server (for custom scripts)
```bash
claude mcp add --transport stdio [name] [command]
```

### Add SSE Server (for streaming data)
```bash
claude mcp add --transport sse [name] [url]
```

## Configuration Features
- Environment variables support
- Authentication headers
- Scope management: local, project, and user levels
- Allowlist/denylist management for organizational deployment

## Best Practices
- Use HTTP servers for remote services
- Use stdio for local custom scripts
- Configure proper authentication and scope management
- Leverage allowlist/denylist for enterprise security
