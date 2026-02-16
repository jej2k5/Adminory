# Plugin Development Guide

## Overview

Adminory's plugin system allows you to extend the framework with custom functionality, widgets, API endpoints, and background tasks.

## Plugin Structure

```
my-plugin/
├── manifest.json           # Plugin metadata and configuration
├── server/                 # Backend code (Python)
│   ├── __init__.py
│   ├── routes.py          # Custom API routes
│   ├── tasks.py           # Background tasks
│   └── hooks.py           # Lifecycle hooks
├── client/                 # Frontend code (React/TypeScript)
│   ├── components/
│   │   └── MyWidget.tsx   # Dashboard widgets
│   └── index.tsx
└── README.md
```

## Plugin Manifest

The `manifest.json` file describes your plugin:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "My awesome plugin",
  "author": "Your Name",
  "homepage": "https://github.com/you/my-plugin",
  "adminory_version": ">=0.1.0",
  "dependencies": {
    "python": ["requests==2.31.0"],
    "npm": ["chart.js@^4.0.0"]
  },
  "permissions": [
    "read:users",
    "write:workspace"
  ],
  "hooks": {
    "on_user_created": "server.hooks:on_user_created",
    "on_workspace_created": "server.hooks:on_workspace_created"
  },
  "routes": [
    {
      "path": "/api/plugins/my-plugin/data",
      "handler": "server.routes:get_data",
      "method": "GET",
      "auth_required": true
    }
  ],
  "widgets": [
    {
      "name": "MyWidget",
      "component": "client/components/MyWidget",
      "control_plane": ["internal", "external"],
      "default_config": {
        "refreshInterval": 60
      }
    }
  ],
  "tasks": [
    {
      "name": "process_plugin_data",
      "handler": "server.tasks:process_data",
      "schedule": "*/5 * * * *"
    }
  ],
  "settings": {
    "api_key": {
      "type": "string",
      "required": true,
      "encrypted": true,
      "label": "API Key"
    },
    "enabled_features": {
      "type": "array",
      "default": [],
      "label": "Enabled Features"
    }
  }
}
```

## Creating a Plugin

### Step 1: Initialize Plugin

```bash
cd plugins/
mkdir my-plugin
cd my-plugin
```

### Step 2: Create Manifest

Create `manifest.json` with your plugin metadata.

### Step 3: Implement Backend Logic

Create `server/routes.py`:

```python
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, get_db

router = APIRouter()

@router.get("/data")
async def get_data(
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    # Your logic here
    return {"data": []}
```

### Step 4: Create Frontend Components

Create `client/components/MyWidget.tsx`:

```typescript
import React from 'react'

interface MyWidgetProps {
  config: {
    refreshInterval: number
  }
}

export default function MyWidget({ config }: MyWidgetProps) {
  return (
    <div className="p-4 border rounded">
      <h3>My Widget</h3>
      {/* Your widget UI */}
    </div>
  )
}
```

### Step 5: Install Plugin

```bash
# Via API
curl -X POST http://localhost:8000/api/plugins/install \
  -H "Authorization: Bearer <token>" \
  -d '{"path": "/path/to/my-plugin"}'

# Or place in plugins/ directory and restart
```

## Plugin Lifecycle Hooks

Available hooks:

- `on_user_created(user)` - Called when a user is created
- `on_workspace_created(workspace)` - Called when a workspace is created
- `on_user_login(user)` - Called on user login
- `on_api_request(request)` - Called before API requests
- `on_api_response(response)` - Called after API responses

Example hook implementation:

```python
# server/hooks.py
from loguru import logger

async def on_user_created(user):
    logger.info(f"Plugin: New user created: {user.email}")
    # Your logic here
```

## Widget Development

Widgets are React components that can be added to dashboards.

**Props passed to widgets:**
- `config` - Widget configuration from manifest
- `workspace` - Current workspace
- `controlPlane` - Current control plane ('internal' or 'external')

**Example widget with API data:**

```typescript
import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'

export default function DataWidget({ config }) {
  const [data, setData] = useState([])

  useEffect(() => {
    const fetchData = async () => {
      const result = await apiClient.get('/api/plugins/my-plugin/data')
      setData(result)
    }

    fetchData()
    const interval = setInterval(fetchData, config.refreshInterval * 1000)
    return () => clearInterval(interval)
  }, [config.refreshInterval])

  return (
    <div>
      {data.map(item => <div key={item.id}>{item.name}</div>)}
    </div>
  )
}
```

## Background Tasks

Plugins can register Celery tasks:

```python
# server/tasks.py
from app.celery_app import celery_app

@celery_app.task(name="my_plugin.process_data")
def process_data():
    # Your task logic
    pass
```

## Plugin Settings

Plugins can define configurable settings:

```json
"settings": {
  "api_key": {
    "type": "string",
    "required": true,
    "encrypted": true,
    "label": "API Key",
    "description": "Your API key for external service"
  }
}
```

Access settings in your plugin:

```python
from app.services.plugin import get_plugin_setting

api_key = await get_plugin_setting('my-plugin', 'api_key', workspace_id)
```

## Testing Plugins

Create `tests/test_plugin.py`:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_plugin_endpoint(client: AsyncClient):
    response = await client.get("/api/plugins/my-plugin/data")
    assert response.status_code == 200
```

## Best Practices

1. **Error Handling**: Always handle errors gracefully
2. **Permissions**: Request only necessary permissions
3. **Performance**: Optimize queries and use caching
4. **Security**: Validate all inputs, sanitize outputs
5. **Documentation**: Provide clear README and examples
6. **Versioning**: Follow semantic versioning
7. **Testing**: Write tests for critical functionality

## Publishing Plugins

TODO: Plugin marketplace coming soon!

---

For more examples, see the [example plugins](../plugins/) directory.
