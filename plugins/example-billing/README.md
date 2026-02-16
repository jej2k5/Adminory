# Example Billing Plugin

A sample plugin demonstrating how to implement billing and usage tracking in Adminory.

## Features

- Usage tracking for API calls
- Invoice generation
- Stripe integration
- Monthly billing automation
- Dashboard widget for billing overview

## Installation

1. Navigate to **External Control Plane > Plugins**
2. Find "Example Billing"
3. Click **Install**
4. Configure Stripe API key in settings

## Configuration

1. Go to **Plugins > Example Billing > Settings**
2. Enter your Stripe API Key
3. Set billing email address
4. Click **Save**

## Usage

### For Workspace Admins

Add the Billing Widget to your dashboard to see:
- Current month usage
- Upcoming invoice amount
- Usage trends
- Payment history

### For Developers

This plugin tracks API usage automatically via hooks:

```python
# Automatically tracks each API request
@hook("on_api_request")
async def track_api_usage(request):
    # Increment usage counter
    pass
```

## API Endpoints

### GET /api/plugins/example-billing/usage

Get usage statistics for current workspace.

**Query Parameters:**
- `start_date` - Start date (ISO format)
- `end_date` - End date (ISO format)

**Response:**
```json
{
  "api_calls": 1234,
  "storage_gb": 5.67,
  "bandwidth_gb": 12.34,
  "cost": 45.67
}
```

### POST /api/plugins/example-billing/invoice

Generate invoice for current billing period.

**Response:**
```json
{
  "invoice_id": "inv_123",
  "amount": 45.67,
  "currency": "USD",
  "status": "pending"
}
```

## Background Tasks

### Generate Monthly Invoices

Runs on the 1st of each month at midnight:
- Calculates usage for previous month
- Generates invoices
- Sends email notifications

## Development

Use this plugin as a template for implementing:
- Third-party API integrations (Stripe, etc.)
- Usage tracking and metering
- Scheduled background tasks
- Encrypted settings storage

## License

MIT
