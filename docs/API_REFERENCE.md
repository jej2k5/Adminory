# Adminory API Reference

## Base URL

```
http://localhost:8000
```

## Authentication

All API endpoints (except public endpoints like `/health` and auth endpoints) require authentication via JWT bearer tokens.

Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Authentication Endpoints

### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "message": "User registered successfully. Please verify your email.",
  "user_id": "uuid"
}
```

### POST /api/auth/login
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
```

### POST /api/auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### POST /api/auth/logout
Logout current user.

**Response:** `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

### GET /api/auth/me
Get current authenticated user.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "workspaces": [...]
}
```

## SSO Endpoints

### GET /api/sso/saml/metadata/:workspace_id
Get SAML Service Provider metadata.

**Response:** `200 OK` (XML)
```xml
<EntityDescriptor ...>
  ...
</EntityDescriptor>
```

### GET /api/sso/saml/login/:workspace_id
Initiate SAML login.

**Response:** `302 Redirect` to IdP

### POST /api/sso/saml/acs/:workspace_id
SAML Assertion Consumer Service (receives SAML response).

**Response:** `302 Redirect` to frontend with tokens

## Internal Control Plane APIs

All internal APIs require `admin` or `super_admin` role.

### GET /api/internal/system/health
Get system health status.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "celery": "running"
}
```

### GET /api/internal/users
List all users (with pagination, search, filters).

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20)
- `search`: Search query
- `role`: Filter by role
- `is_active`: Filter by active status

**Response:** `200 OK`
```json
{
  "users": [...],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

### GET /api/internal/users/:id
Get user details.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "workspaces": [...]
}
```

## External Control Plane APIs

### GET /api/external/workspace
Get current workspace details.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "Acme Corp",
  "slug": "acme-corp",
  "plan": "enterprise",
  "sso_enabled": true
}
```

### GET /api/external/workspace/members
List workspace members.

**Response:** `200 OK`
```json
{
  "members": [
    {
      "id": "uuid",
      "user": {...},
      "role": "admin",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /api/external/workspace/members
Invite member to workspace.

**Request Body:**
```json
{
  "email": "newmember@example.com",
  "role": "member"
}
```

**Response:** `201 Created`
```json
{
  "message": "Invitation sent",
  "invite_id": "uuid"
}
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "status_code": 400
}
```

### Common Error Codes

- `400` - Bad Request
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Validation Error
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

---

For complete API documentation, visit: http://localhost:8000/docs (Swagger UI)
