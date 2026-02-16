# Adminory Architecture

## Overview

Adminory is built as a dual control plane system with a clear separation between internal operations and external customer-facing interfaces. This document describes the high-level architecture and design decisions.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js 14)                 │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │  Internal Control    │      │  External Control    │    │
│  │      Plane UI        │      │      Plane UI        │    │
│  └──────────────────────┘      └──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/WSS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │  Internal APIs       │      │  External APIs       │    │
│  │  /api/internal/*     │      │  /api/external/*     │    │
│  └──────────────────────┘      └──────────────────────┘    │
│                                                               │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │   MCP Server         │      │   SSO Integration    │    │
│  │   (Internal/External)│      │   (SAML/OAuth)       │    │
│  └──────────────────────┘      └──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
        ┌──────────────┐      ┌──────────────┐
        │  PostgreSQL  │      │    Redis     │
        │   Database   │      │   Cache      │
        └──────────────┘      └──────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │    Celery    │
                              │  (Workers)   │
                              └──────────────┘
```

## Core Components

### 1. Frontend (Next.js 14)

**Technology**: Next.js 14 with App Router, TypeScript, TailwindCSS, shadcn/ui

**Structure**:
- **Internal Control Plane** (`/internal/*`)
  - System monitoring and health
  - User and workspace management
  - Audit log viewing
  - Feature flag management
  - SSO configuration (admin)

- **External Control Plane** (`/external/*`)
  - Workspace settings
  - Team management
  - Usage analytics
  - API key management
  - SSO setup (customer)

**Key Features**:
- Server-side rendering (SSR) for SEO and performance
- Client-side navigation for SPA experience
- Real-time updates via WebSockets
- Responsive design with TailwindCSS
- Type-safe with TypeScript

### 2. Backend (FastAPI)

**Technology**: Python 3.11+, FastAPI, SQLAlchemy, Alembic

**Structure**:
- RESTful API endpoints
- WebSocket support for real-time features
- Middleware stack (auth, RBAC, rate limiting, audit)
- Service layer for business logic
- Repository pattern for data access

**API Design**:
- `/api/auth/*` - Authentication endpoints
- `/api/sso/*` - SSO endpoints (SAML/OAuth)
- `/api/internal/*` - Internal control plane APIs
- `/api/external/*` - External control plane APIs
- `/api/mcp/*` - MCP protocol endpoints

**Middleware Stack** (executed in order):
1. CORS middleware
2. Rate limiting
3. Authentication (JWT validation)
4. Workspace context
5. Control plane separation
6. RBAC enforcement
7. Audit logging

### 3. Database (PostgreSQL 15+)

**Schema Organization**:
- Core tables: `users`, `workspaces`, `workspace_members`
- SSO tables: `sso_configurations`, `sso_saml_configs`, `sso_oauth_configs`
- Feature tables: `feature_flags`, `plugins`, `widgets`
- Monitoring: `audit_logs`, `system_metrics`, `events`
- Support: `support_tickets`, `support_messages`

**Key Design Decisions**:
- UUID primary keys for security and distributed systems
- JSONB columns for flexible metadata storage
- Proper foreign key constraints with cascading deletes
- Indexes on frequently queried columns
- Workspace isolation enforced at query level

### 4. Cache & Queue (Redis)

**Use Cases**:
- Session storage
- Cache layer for expensive queries
- Rate limiting counters
- Pub/sub for real-time updates
- Celery message broker

### 5. Background Jobs (Celery)

**Tasks**:
- Email sending
- Analytics processing
- Data cleanup
- Report generation
- Scheduled maintenance

**Configuration**:
- Task retries with exponential backoff
- Task priorities
- Periodic tasks via Celery Beat
- Result backend for task status tracking

### 6. Enterprise SSO

**Supported Protocols**:
- SAML 2.0 (Service Provider implementation)
- OAuth 2.0 / OpenID Connect

**Features**:
- Per-workspace SSO configuration
- Multiple IdP support (Okta, Azure AD, Google, etc.)
- JIT user provisioning
- Attribute/group mapping
- Domain-based SSO discovery
- Fallback authentication

**Security**:
- SAML assertion validation
- Signature verification
- OAuth state parameter
- Token refresh
- Encrypted credential storage

### 7. MCP Integration

**Internal MCP Server**:
- Tools for system administration
- User and workspace management
- Audit log queries
- Database read queries
- SSO configuration assistance

**External MCP Server**:
- Tools for customer self-service
- Workspace management
- Usage analytics
- Integration setup
- Support ticket creation

### 8. Plugin System

**Architecture**:
- Plugin manifest (JSON)
- Server-side hooks (Python)
- Client-side components (React)
- Isolated execution environment
- Plugin registry

**Extension Points**:
- Custom API endpoints
- Dashboard widgets
- Background tasks
- Database migrations
- Settings pages

## Data Flow

### Authentication Flow (Email/Password)

```
User → Frontend → POST /api/auth/login
                    ↓
              Validate credentials
                    ↓
              Generate JWT tokens
                    ↓
              Return access + refresh tokens
                    ↓
Frontend stores tokens → Subsequent requests include token
```

### SSO Authentication Flow (SAML)

```
User → Frontend → Detect email domain
                    ↓
              GET /api/sso/saml/login/:workspace_id
                    ↓
              Generate SAML AuthnRequest
                    ↓
              Redirect to IdP
                    ↓
User authenticates at IdP
                    ↓
              IdP sends SAML assertion
                    ↓
              POST /api/sso/saml/acs/:workspace_id
                    ↓
              Validate assertion + signature
                    ↓
              JIT provision user if needed
                    ↓
              Generate JWT tokens
                    ↓
              Redirect to frontend with tokens
```

### Workspace Isolation

All workspace-scoped queries include workspace_id:
```python
query = select(Resource).where(
    Resource.workspace_id == current_workspace_id
)
```

Middleware enforces workspace context:
```python
# Get workspace from JWT or header
workspace_id = get_current_workspace(request)

# Validate user has access to workspace
if not user_has_workspace_access(user, workspace_id):
    raise HTTPException(403)

# Inject into request state
request.state.workspace_id = workspace_id
```

## Security Architecture

### Authentication & Authorization

**JWT Strategy**:
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (7 days)
- Refresh token rotation on use
- Tokens include user ID, workspace ID, roles

**RBAC Model**:
- Global roles: `super_admin`, `admin`, `user`
- Workspace roles: `owner`, `admin`, `member`, `viewer`
- Permission checks at API endpoint level
- Row-level security via workspace_id filtering

### Data Protection

**At Rest**:
- Database encryption (PostgreSQL TDE)
- Sensitive fields encrypted (SSO credentials, API keys)
- Encryption key rotation support

**In Transit**:
- HTTPS/TLS for all communication
- WSS for WebSocket connections
- Certificate management

**Secrets Management**:
- Environment variables for configuration
- Encrypted storage for SSO secrets
- No secrets in code or logs

### Audit Logging

Every sensitive action is logged:
```python
audit_log = AuditLog(
    workspace_id=workspace_id,
    user_id=user_id,
    action="user.update",
    resource_type="user",
    resource_id=target_user_id,
    metadata={"changes": changes},
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent"),
)
```

Logs are:
- Immutable (no updates/deletes)
- Retained for compliance period
- Searchable and exportable
- Include SSO session tracking

## Scalability Considerations

### Horizontal Scaling

**Backend**:
- Stateless API servers
- Load balancer distribution
- Shared session storage (Redis)
- Database connection pooling

**Database**:
- Read replicas for analytics queries
- Connection pooling (PgBouncer)
- Query optimization and indexing
- Partitioning for large tables (audit_logs)

**Cache**:
- Redis cluster for high availability
- Cache warming strategies
- TTL management

### Vertical Scaling

- Resource allocation per service
- Auto-scaling based on metrics
- Resource limits via Docker/K8s

### Performance Optimization

**Backend**:
- Async/await throughout
- Database query optimization
- N+1 query prevention
- Pagination on all list endpoints
- Background jobs for slow operations

**Frontend**:
- Code splitting
- Lazy loading
- Image optimization
- Caching strategies
- Debounced search

## Deployment Architecture

### Development
```
docker-compose up
  ├── postgres (single instance)
  ├── redis (single instance)
  ├── backend (hot-reload)
  ├── celery worker
  ├── celery beat
  └── frontend (dev server)
```

### Production (Docker Swarm)
```
Load Balancer
  ├── Frontend (3+ replicas)
  │     └── Static assets on CDN
  ├── Backend (3+ replicas)
  │     └── Health checks
  ├── Celery Workers (2+ replicas)
  └── Celery Beat (1 replica)

Database (PostgreSQL)
  ├── Primary (write)
  └── Replicas (read)

Cache (Redis)
  ├── Master
  └── Replicas
```

### Production (Kubernetes)
- Deployments for each service
- HorizontalPodAutoscaler
- Services for internal communication
- Ingress for external access
- ConfigMaps and Secrets
- PersistentVolumeClaims for database

## Monitoring & Observability

### Metrics
- Application metrics (Prometheus)
- System metrics (CPU, memory, disk)
- Business metrics (MAU, API calls)
- Error rates and latency

### Logging
- Structured logging (Loguru)
- Centralized log aggregation
- Log levels per environment
- Search and filtering

### Tracing
- Request tracing (OpenTelemetry)
- Distributed tracing across services
- Performance profiling

### Alerting
- Health check failures
- Error rate thresholds
- Resource utilization
- SSO authentication failures

## Future Enhancements

- GraphQL API option
- Multi-region deployment
- SCIM provisioning
- Advanced RBAC with custom policies
- Mobile app (React Native)
- Plugin marketplace
- Terraform modules
- Kubernetes operators

---

For more details, see:
- [Plugin Development Guide](./PLUGIN_DEVELOPMENT.md)
- [MCP Integration Guide](./MCP_INTEGRATION.md)
- [SSO Setup Guide](./SSO_SETUP_GUIDE.md)
- [Deployment Guide](./DEPLOYMENT.md)
