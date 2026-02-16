# Example Analytics Plugin

A sample plugin demonstrating how to create custom analytics widgets in Adminory.

## Features

- Custom dashboard widget with charts
- Analytics API endpoint
- User login tracking hook

## Installation

This plugin is included as an example. To install:

1. Navigate to **Internal Control Plane > Plugins**
2. Find "Example Analytics"
3. Click **Enable**

## Usage

Once enabled, add the Analytics Chart widget to your dashboard:

1. Go to your dashboard
2. Click **Add Widget**
3. Select **Analytics Chart**
4. Configure refresh interval and chart type

## Development

This plugin serves as a template for creating your own plugins.

### File Structure

```
example-analytics/
├── manifest.json           # Plugin metadata
├── server/                 # Backend Python code
│   ├── __init__.py
│   ├── routes.py          # API endpoints
│   └── hooks.py           # Lifecycle hooks
├── client/                 # Frontend React components
│   └── components/
│       └── AnalyticsChart.tsx
└── README.md
```

### Extending

To modify this plugin:

1. Update `manifest.json` with your changes
2. Implement custom logic in `server/` files
3. Create React components in `client/`
4. Restart Adminory to reload plugin

## API Endpoints

### GET /api/plugins/example-analytics/stats

Returns analytics statistics.

**Response:**
```json
{
  "total_users": 100,
  "active_users": 50,
  "total_api_calls": 10000
}
```

## License

MIT
