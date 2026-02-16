# Deployment Guide

## Overview

This guide covers deploying Adminory in various environments, from development to production.

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 15+ database
- Redis 7+ server
- SSL certificate (for production)
- Domain name (for production)

## Development Deployment

### Using Docker Compose

```bash
# Clone repository
git clone https://github.com/yourusername/adminory.git
cd adminory

# Copy environment file
cp .env.example .env

# Edit .env and set secure values for:
# - JWT_SECRET (min 32 characters)
# - JWT_REFRESH_SECRET (min 32 characters)
# - ENCRYPTION_KEY (exactly 32 characters)
nano .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development (Without Docker)

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up environment
cp ../.env.example .env
# Edit .env with local database/Redis URLs

# Start PostgreSQL and Redis (if not using Docker)
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker (new terminal)
celery -A app.celery_app worker --loglevel=info

# Start Celery beat (new terminal)
celery -A app.celery_app beat --loglevel=info
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp ../.env.example .env.local
# Edit NEXT_PUBLIC_API_URL if needed

# Start development server
npm run dev
```

## Production Deployment

### Option 1: Docker Compose (Single Server)

**Step 1: Prepare Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Step 2: Configure Application**
```bash
# Clone repository
git clone https://github.com/yourusername/adminory.git
cd adminory

# Create production environment file
cp .env.example .env

# Edit with production values
nano .env
```

**Critical .env settings for production:**
```env
ENVIRONMENT=production
DEBUG=false

# Generate secure secrets (use openssl or similar)
JWT_SECRET=$(openssl rand -base64 32)
JWT_REFRESH_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32 | cut -c1-32)
SECRET_KEY=$(openssl rand -base64 32)

# Database (use strong password)
DATABASE_URL=postgresql://adminory:STRONG_PASSWORD@postgres:5432/adminory

# CORS (your domain)
CORS_ORIGINS=https://your-domain.com

# SSO (your domain)
SSO_BASE_URL=https://your-domain.com

# Email configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
SMTP_FROM=noreply@your-domain.com
```

**Step 3: Set Up SSL**

Using Let's Encrypt with Nginx reverse proxy:

```bash
# Install Nginx
sudo apt install nginx certbot python3-certbot-nginx -y

# Configure Nginx
sudo nano /etc/nginx/sites-available/adminory
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://localhost:8000;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/adminory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

**Step 4: Start Application**
```bash
docker-compose -f docker-compose.yml up -d
```

**Step 5: Initialize Database**
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create superuser (optional)
docker-compose exec backend python -m app.cli create-superuser \
  --email admin@your-domain.com \
  --password SECURE_PASSWORD \
  --name "Admin User"
```

### Option 2: Kubernetes Deployment

**Prerequisites:**
- Kubernetes cluster (EKS, GKE, AKS, or self-hosted)
- kubectl configured
- Helm 3.x

**Step 1: Create Namespace**
```bash
kubectl create namespace adminory
```

**Step 2: Create Secrets**
```bash
kubectl create secret generic adminory-secrets \
  --from-literal=jwt-secret=$(openssl rand -base64 32) \
  --from-literal=jwt-refresh-secret=$(openssl rand -base64 32) \
  --from-literal=encryption-key=$(openssl rand -base64 32 | cut -c1-32) \
  --from-literal=database-password=$(openssl rand -base64 32) \
  -n adminory
```

**Step 3: Deploy PostgreSQL**
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install adminory-postgres bitnami/postgresql \
  --set auth.username=adminory \
  --set auth.password=$(kubectl get secret adminory-secrets -n adminory -o jsonpath='{.data.database-password}' | base64 -d) \
  --set auth.database=adminory \
  -n adminory
```

**Step 4: Deploy Redis**
```bash
helm install adminory-redis bitnami/redis \
  --set auth.enabled=false \
  -n adminory
```

**Step 5: Deploy Application**

Create `k8s/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adminory-backend
  namespace: adminory
spec:
  replicas: 3
  selector:
    matchLabels:
      app: adminory-backend
  template:
    metadata:
      labels:
        app: adminory-backend
    spec:
      containers:
      - name: backend
        image: your-registry/adminory-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://adminory:$(DATABASE_PASSWORD)@adminory-postgres:5432/adminory"
        - name: REDIS_URL
          value: "redis://adminory-redis:6379"
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: adminory-secrets
              key: jwt-secret
        # ... more env vars
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

Apply:
```bash
kubectl apply -f k8s/
```

### Option 3: Cloud Platform Deployment

**AWS ECS:**
- Use AWS ECS with Fargate
- RDS for PostgreSQL
- ElastiCache for Redis
- Application Load Balancer
- Route53 for DNS
- ACM for SSL certificates

**Google Cloud Run:**
- Cloud Run for backend/frontend
- Cloud SQL for PostgreSQL
- Memorystore for Redis
- Cloud Load Balancing
- Cloud DNS

**Azure Container Instances:**
- Azure Container Instances
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Azure Application Gateway
- Azure DNS

## Database Migrations

**Run migrations:**
```bash
# Docker
docker-compose exec backend alembic upgrade head

# Kubernetes
kubectl exec -it deployment/adminory-backend -n adminory -- alembic upgrade head

# Local
cd backend
alembic upgrade head
```

**Create new migration:**
```bash
alembic revision --autogenerate -m "Description of changes"
```

## Monitoring & Logging

### Health Checks

- Backend health: `GET /health`
- System status: `GET /api/internal/system/health` (requires auth)

### Logging

Configure log level:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json # json or text
```

### Metrics (Future)

- Prometheus metrics endpoint: `/metrics`
- Grafana dashboards for visualization

## Backups

### Database Backups

**Automated backups:**
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)

docker-compose exec -T postgres pg_dump -U adminory adminory | \
  gzip > $BACKUP_DIR/adminory_$DATE.sql.gz

# Keep last 30 days
find $BACKUP_DIR -name "adminory_*.sql.gz" -mtime +30 -delete
```

**Restore from backup:**
```bash
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U adminory adminory
```

### File Backups

Backup volumes:
```bash
docker-compose stop
tar -czf volumes_backup.tar.gz -C /var/lib/docker/volumes .
docker-compose start
```

## Scaling

### Horizontal Scaling

**Backend:**
- Run multiple backend replicas
- Use load balancer
- Share Redis for sessions
- Database connection pooling

**Celery Workers:**
```bash
# Scale workers
docker-compose up -d --scale celery_worker=5
```

**Frontend:**
- Multiple frontend replicas
- CDN for static assets
- Edge caching

### Vertical Scaling

Adjust resource limits in docker-compose.yml:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Security Checklist

- [ ] Change all default secrets
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Enable database encryption
- [ ] Set up regular backups
- [ ] Configure rate limiting
- [ ] Review CORS settings
- [ ] Enable audit logging
- [ ] Keep dependencies updated
- [ ] Monitor security advisories

## Troubleshooting

**Database connection errors:**
- Verify DATABASE_URL
- Check PostgreSQL is running
- Verify network connectivity

**Redis connection errors:**
- Check REDIS_URL
- Verify Redis is running
- Check Redis max connections

**Frontend can't connect to backend:**
- Verify NEXT_PUBLIC_API_URL
- Check CORS_ORIGINS configuration
- Verify network/firewall rules

**Celery tasks not running:**
- Check Celery worker logs
- Verify Redis connection
- Check task queue

---

For more help, see:
- [Architecture Documentation](./ARCHITECTURE.md)
- [API Reference](./API_REFERENCE.md)
- [GitHub Issues](https://github.com/yourusername/adminory/issues)
