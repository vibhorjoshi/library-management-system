# Docker Build & Run Guide

## Quick Start

### 1. Prerequisites
```bash
# Install Docker and Docker Compose
# macOS/Windows: Download Docker Desktop
# Linux: sudo apt-get install docker.io docker-compose
```

### 2. Setup Environment
```bash
# Copy and configure environment variables
cp .env.docker .env

# Edit .env and set your values
nano .env
```

### 3. Build and Run Everything
```bash
# Build all images
docker-compose build

# Start all services
docker-compose up

# Run in background
docker-compose up -d
```

### 4. Access Services
```
Backend API:    http://localhost:8000
Frontend:       http://localhost:3000
Admin Panel:    http://localhost:8000/admin
Database:       localhost:3306 (MySQL)
Redis Cache:    localhost:6379
```

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Database Management
```bash
# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Run migrations
docker-compose exec backend python manage.py migrate

# Make migrations
docker-compose exec backend python manage.py makemigrations

# Database shell
docker-compose exec db mysql -u library_user -p library_db
```

### Frontend Management
```bash
# Install dependencies
docker-compose exec frontend npm install

# Rebuild frontend
docker-compose exec frontend npm run build
```

### Stop Services
```bash
# Stop all running services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove all including volumes (WARNING: deletes data)
docker-compose down -v
```

## Troubleshooting

### Database Connection Failed
```bash
# Check if database is running
docker-compose ps

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Port Already in Use
```bash
# Change port in docker-compose.yml
# ports:
#   - "8001:8000"  # Use 8001 instead of 8000
```

### Rebuild After Code Changes
```bash
# Rebuild images
docker-compose build --no-cache

# Restart services
docker-compose up
```

### Clear Cache
```bash
# Prune unused images
docker system prune

# Remove all images
docker rmi $(docker images -q)
```

## Production Deployment

### Use Environment Variables
```bash
# Create separate production .env
cp .env.docker .env.prod

# Edit with production values
nano .env.prod
```

### Enable HTTPS
```yaml
# Add reverse proxy (Nginx) to docker-compose.yml
nginx:
  image: nginx:latest
  ports:
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
```

### Scale Services
```bash
# Run multiple backend instances
docker-compose up -d --scale backend=3
```

## Performance Tips

1. **Use `.dockerignore`** to exclude unnecessary files
2. **Enable BuildKit** for faster builds
   ```bash
   export DOCKER_BUILDKIT=1
   ```
3. **Use Multi-stage builds** (already implemented in frontend)
4. **Limit container resources**
   ```yaml
   resources:
     limits:
       cpus: '0.5'
       memory: 512M
   ```

## Health Checks

Services have automatic health checks:
- Database: Checks MySQL connectivity
- Backend: Waits for database to be healthy
- Frontend: Always available

Monitor health:
```bash
docker-compose ps
```

## Persistent Data

Data is stored in Docker volumes:
- `mysql_data` - Database files
- `redis_data` - Cache data
- `./staticfiles` - Static files
- `./media` - User uploads

View volumes:
```bash
docker volume ls
docker volume inspect library-management-system_mysql_data
```
