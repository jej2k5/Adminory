# MCP Integration Guide

## Overview

Adminory integrates with the Model Context Protocol (MCP) to enable AI-powered administrative tasks through Claude and other AI assistants.

## Architecture

Adminory provides two separate MCP servers:

1. **Internal MCP Server** - For operations teams
2. **External MCP Server** - For customers

Each server exposes different tools based on the control plane context.

## Internal MCP Tools

Available to operations teams and administrators:

### System Tools
- `get_system_health` - Get system health status
- `get_system_metrics` - Query system metrics
- `get_database_stats` - Database connection and performance stats

### User Tools
- `search_users` - Search for users
- `get_user_details` - Get detailed user information
- `impersonate_user` - Impersonate a user (audit logged)

### Audit Tools
- `search_audit_logs` - Search audit logs with filters
- `get_audit_log_details` - Get detailed audit log entry

### Query Tools
- `execute_read_query` - Execute read-only SQL queries
- `get_table_schema` - Get database table schema

### SSO Tools
- `list_sso_configs` - List all SSO configurations
- `test_sso_connection` - Test SSO connection

## External MCP Tools

Available to customers in their workspace:

### Workspace Tools
- `get_workspace_details` - Get workspace information
- `update_workspace_settings` - Update workspace settings
- `invite_team_member` - Invite new team member

### Analytics Tools
- `get_usage_metrics` - Get workspace usage metrics
- `get_active_users` - Get active users count

### Integration Tools
- `list_integrations` - List configured integrations
- `test_integration` - Test integration connection

### SSO Tools (Enterprise)
- `get_sso_config` - Get workspace SSO configuration
- `update_sso_config` - Update SSO configuration
- `test_sso_setup` - Test SSO setup

### Support Tools
- `create_support_ticket` - Create a support ticket
- `list_support_tickets` - List support tickets

## Using MCP with Claude Desktop

### Step 1: Configure MCP Server

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "adminory-internal": {
      "command": "http",
      "args": ["POST", "http://localhost:8000/api/mcp/internal/tools/call"],
      "headers": {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN"
      }
    },
    "adminory-external": {
      "command": "http",
      "args": ["POST", "http://localhost:8000/api/mcp/external/tools/call"],
      "headers": {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        "X-Workspace-ID": "YOUR_WORKSPACE_ID"
      }
    }
  }
}
```

### Step 2: Use Tools in Claude

Example prompts:

**Internal Control Plane:**
```
Search for users with email containing "example.com"
```

**External Control Plane:**
```
Show me my workspace's usage metrics for the last 30 days
```

## Implementing Custom MCP Tools

### Backend Tool Implementation

Create a new tool in `app/mcp/internal/` or `app/mcp/external/`:

```python
# app/mcp/internal/custom_tools.py
from typing import Dict, Any
from app.mcp.server import MCPTool

class MyCustomTool(MCPTool):
    name = "my_custom_tool"
    description = "Description of what this tool does"

    async def execute(
        self,
        params: Dict[str, Any],
        user_id: str,
        workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the tool.

        Args:
            params: Tool parameters
            user_id: Current user ID
            workspace_id: Current workspace ID (if applicable)

        Returns:
            Tool execution result
        """
        # Your implementation here
        return {"result": "success"}
```

### Register Tool

```python
# app/mcp/internal/__init__.py
from .custom_tools import MyCustomTool

INTERNAL_TOOLS = [
    MyCustomTool(),
    # ... other tools
]
```

## MCP Tool Best Practices

1. **Clear Descriptions**: Write clear tool descriptions for the AI
2. **Input Validation**: Validate all parameters
3. **Error Handling**: Return meaningful error messages
4. **Audit Logging**: Log sensitive operations
5. **Performance**: Keep tools fast (< 5 seconds)
6. **Permissions**: Check user permissions before execution

## Example MCP Workflows

### User Management Workflow

```
Prompt: "Find all inactive users who haven't logged in for 90 days"

Claude uses:
1. search_users(is_active=true, last_login_before="90 days ago")
2. Returns list of users
3. Formats response for human
```

### SSO Setup Workflow

```
Prompt: "Help me set up SAML SSO with Okta"

Claude uses:
1. get_sso_config() - Check current config
2. Guides through Okta setup
3. update_sso_config() - Save configuration
4. test_sso_setup() - Verify it works
```

## API Endpoints

### POST /api/mcp/internal/tools/list
List available internal tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "search_users",
      "description": "Search for users",
      "parameters": {...}
    }
  ]
}
```

### POST /api/mcp/internal/tools/call
Execute an internal tool.

**Request:**
```json
{
  "tool": "search_users",
  "parameters": {
    "query": "john"
  }
}
```

**Response:**
```json
{
  "result": {
    "users": [...]
  }
}
```

## Security Considerations

- All MCP calls require authentication
- Internal tools require admin role
- External tools are workspace-scoped
- Sensitive operations are audit logged
- Rate limiting applies to MCP endpoints

---

For implementation details, see the [MCP source code](../backend/app/mcp/).
