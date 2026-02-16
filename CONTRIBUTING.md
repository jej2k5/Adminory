# Contributing to Adminory

Thank you for considering contributing to Adminory!

## 🐛 Reporting Bugs

- Use GitHub issues
- Include detailed steps to reproduce
- Provide environment details (OS, Python version, Docker version)
- Include error messages and logs
- Specify which control plane (internal/external)
- For SSO issues, specify the IdP and protocol (SAML/OAuth)

## 💡 Suggesting Features

- Use GitHub issues with "enhancement" label
- Describe the use case clearly
- Explain benefits for users
- Consider implementation complexity
- Specify if it's for internal, external, or both control planes

## 🔧 Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Write/update tests
5. Ensure tests pass: `pytest` (backend) and `npm test` (frontend)
6. Update documentation
7. Commit using Conventional Commits: `git commit -m "feat: add amazing feature"`
8. Push: `git push origin feature/amazing-feature`
9. Open a Pull Request

## 📝 Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Test updates
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements

## 🎨 Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints everywhere
- Maximum line length: 100 characters
- Use Black for formatting
- Use isort for import sorting
- Write docstrings (Google style)
- Use async/await with FastAPI

### TypeScript/React (Frontend)
- Use TypeScript strict mode
- Write meaningful variable names
- Use functional components
- Use hooks for state management
- Memoize expensive computations
- Follow Next.js App Router conventions

## 🧪 Testing

### Backend Testing
- Write tests for new features
- Maintain >70% code coverage
- Use pytest fixtures
- Use descriptive test names
- Test both success and error cases
- Mock external services (SSO IdPs, email, etc.)

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_sso.py

# Run with verbose output
pytest -v
```

### Frontend Testing
- Use Jest and React Testing Library
- Test user interactions
- Test error states
- Mock API calls

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage
```

## 📚 Plugin Development

If creating a plugin:
- Follow the plugin development guide
- Include a comprehensive manifest.json
- Provide example usage
- Document all configuration options
- Test in both control planes if applicable
- Include unit tests

## 🔒 Security

- Never commit secrets or credentials
- Use environment variables for config
- Follow OWASP security guidelines
- Validate all user inputs
- Use parameterized queries
- Report security issues privately to maintainers
- For SSO: Always validate signatures and assertions

## 🏗️ Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/adminory.git
cd adminory

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Frontend setup
cd ../frontend
npm install

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Start development environment
docker-compose up -d postgres redis

# Run migrations
cd backend
alembic upgrade head

# Run backend
uvicorn app.main:app --reload

# Run Celery (new terminal)
celery -A app.celery_app worker --loglevel=info

# Run frontend (new terminal)
cd frontend
npm run dev
```

## 📖 Documentation

When adding features:
- Update relevant documentation in `/docs`
- Update API reference if adding endpoints
- Update MCP guide if adding MCP tools
- Update plugin guide if extending plugin API
- Update SSO guide if modifying SSO functionality
- Include code examples
- Add docstrings to all functions/classes

## ❓ Questions?

- Open an issue with the "question" label
- Join our discussions on GitHub
- Check existing documentation first

## 🎉 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Featured in the README (for significant contributions)

Thank you for making Adminory better! 🚀
