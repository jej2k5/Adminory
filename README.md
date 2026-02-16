# Adminory - Universal Admin Control Plane Framework

An open-source, production-ready framework for building admin control planes with dual interfaces (internal ops + external customer), enterprise SSO, MCP integration, and extensible plugin architecture.

## ✨ Features

- **Dual Control Planes**: Separate internal (ops) and external (customer) admin interfaces
- **Enterprise SSO**: Full SAML 2.0 and OAuth 2.0/OIDC support with major IdP compatibility
- **MCP Integration**: AI-powered admin assistance via Model Context Protocol
- **Plugin System**: Extensible architecture with custom widgets and functionality
- **Multi-Tenancy**: Complete workspace isolation and management
- **Real-time Analytics**: Live dashboards with WebSocket updates
- **Role-Based Access Control**: Granular permissions across workspaces
- **Background Jobs**: Celery-based task processing
- **Audit Logging**: Comprehensive activity tracking
- **Feature Flags**: Dynamic feature control per workspace
- **API-First**: Full REST API + MCP protocol support built with FastAPI
- **Self-Hostable**: Docker-based deployment
- **Open Source**: MIT License

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend local development)

### Running with Docker

```bash
git clone https://github.com/yourusername/adminory.git
cd adminory
cp .env.example .env
# Edit .env with your configuration (IMPORTANT: Change all secret keys!)
docker-compose up -d
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Local Development

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Frontend setup
cd ../frontend
npm install

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Start database and Redis
docker-compose up -d postgres redis

# Run Alembic migrations
cd backend
alembic upgrade head

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Celery worker (new terminal)
celery -A app.celery_app worker --loglevel=info

# Run Celery beat (new terminal)
celery -A app.celery_app beat --loglevel=info

# Run frontend (new terminal)
cd frontend
npm run dev
```

## 📁 Project Structure

```
adminory/
├── backend/          # FastAPI backend
│   ├── app/          # Application code
│   ├── alembic/      # Database migrations
│   └── tests/        # Backend tests
├── frontend/         # Next.js frontend
│   └── src/          # Frontend code
├── plugins/          # Example plugins
├── database/         # DB initialization
├── docs/             # Documentation
├── docker-compose.yml
└── README.md
```

## 🎯 Core Concepts

### Dual Control Planes

**Internal Control Plane** (`/internal`)
- For operations teams and support staff
- Full system visibility
- User impersonation
- System monitoring
- Advanced analytics
- SSO configuration management

**External Control Plane** (`/external`)
- For end customers
- Workspace management
- Team administration
- Usage analytics
- Self-service features
- SSO setup (enterprise plan)

### Enterprise SSO

Adminory supports enterprise-grade SSO with:

**SAML 2.0**
- Compatible with Okta, Azure AD, Google Workspace, OneLogin
- Automatic metadata exchange
- JIT (Just-In-Time) user provisioning
- Attribute mapping
- Single Logout (SLO)

**OAuth 2.0 / OpenID Connect**
- OAuth authorization code flow
- OIDC discovery and validation
- Token exchange and refresh
- Userinfo endpoint integration

**SSO Features**
- Per-workspace SSO configuration
- Domain-based SSO auto-discovery
- SSO enforcement policies
- Fallback to email/password
- Test SSO connection functionality

See [SSO_SETUP_GUIDE.md](./docs/SSO_SETUP_GUIDE.md) for detailed setup instructions.

### MCP Integration

Adminory includes MCP servers for both control planes:
- **Internal MCP**: System queries, user management, audit logs, SSO config
- **External MCP**: Workspace operations, usage analytics, support, SSO setup

See [MCP_INTEGRATION.md](./docs/MCP_INTEGRATION.md) for details.

### Plugin System

Extend Adminory with custom functionality:
- Custom widgets for dashboards
- New API endpoints
- Background jobs
- Database extensions

See [PLUGIN_DEVELOPMENT.md](./docs/PLUGIN_DEVELOPMENT.md) for guide.

## 📖 Documentation

- [Architecture Overview](./docs/ARCHITECTURE.md)
- [API Reference](./docs/API_REFERENCE.md)
- [Plugin Development Guide](./docs/PLUGIN_DEVELOPMENT.md)
- [MCP Integration Guide](./docs/MCP_INTEGRATION.md)
- [SSO Setup Guide](./docs/SSO_SETUP_GUIDE.md)
  - [Okta SAML Setup](./docs/sso/OKTA_SAML.md)
  - [Azure AD SAML Setup](./docs/sso/AZURE_AD_SAML.md)
  - [Google Workspace Setup](./docs/sso/GOOGLE_WORKSPACE.md)
  - [Generic SAML Setup](./docs/sso/GENERIC_SAML.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Contributing Guidelines](./CONTRIBUTING.md)

## 🔧 Configuration

Key environment variables:
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `JWT_SECRET` - JWT signing key (min 32 chars)
- `ENCRYPTION_KEY` - Data encryption key (exactly 32 chars)
- `SSO_ENABLED` - Enable/disable SSO
- `MCP_ENABLED` - Enable/disable MCP servers
- `PLUGINS_ENABLED` - Enable/disable plugin system

See `.env.example` for complete list.

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
npm run test:coverage
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](./LICENSE)

## 💬 Support

- Issues: [GitHub Issues](https://github.com/yourusername/adminory/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/adminory/discussions)
- Documentation: [docs/](./docs/)

## 🗺️ Roadmap

- [ ] Additional SSO providers (LDAP, CAS)
- [ ] Multi-region deployment support
- [ ] GraphQL API option
- [ ] Mobile app (React Native)
- [ ] Advanced RBAC with custom policies
- [ ] Kubernetes deployment templates
- [ ] Terraform modules
- [ ] Plugin marketplace
- [ ] SCIM provisioning support

## 🏆 Why Adminory?

Built by developers who were tired of rebuilding admin interfaces for every project. Adminory provides:

- **Reusability**: One framework, multiple projects
- **Enterprise-Ready**: SSO, audit logs, RBAC out of the box
- **AI-Powered**: MCP integration for intelligent assistance
- **Extensible**: Plugin system for unlimited customization
- **Production-Tested**: Battle-tested patterns and security

---

**Built with ❤️ by the Adminory team**
