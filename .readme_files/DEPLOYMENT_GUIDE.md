# DEPLOYMENT GUIDE - Library Management System

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       PRODUCTION DEPLOYMENT                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Frontend (React)           Backend (Django)      Database       │
│  ┌──────────────┐          ┌──────────────┐      ┌──────────┐  │
│  │ Vercel/AWS  │ ◄──────► │   Heroku/    │ ◄───► │ MySQL/   │  │
│  │  S3 + CDN   │ (HTTPS)  │   Railway    │       │ PostgreSQL  │
│  └──────────────┘          └──────────────┘      └──────────┘  │
│         ▲                         ▲                       ▲      │
│         │                         │                       │      │
│    Static Assets            REST APIs              SQL Queries   │
│    (JS, CSS, HTML)         (JWT Auth)             (ORM/Raw SQL)  │
│                                                                   │
│  Email Service              Cache Layer         Monitoring       │
│  ┌──────────────┐          ┌──────────┐        ┌────────────┐   │
│  │  Gmail/      │          │ Redis    │        │ Sentry/    │   │
│  │  SendGrid    │          │ (Caching)│        │ New Relic  │   │
│  └──────────────┘          └──────────┘        └────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Phase 1: Backend Deployment (Django)

### Option A: Deploy to Heroku (Recommended for beginners)

#### Prerequisites
- Heroku Account (free tier available)
- Heroku CLI installed
- Git repository initialized

#### Step 1: Prepare Django for Production

Update `settings.py`:
```python
# Production security settings
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database (uses DATABASE_URL environment variable)
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

Create `Procfile`:
```
web: gunicorn library_config.wsgi
```

Create `runtime.txt`:
```
python-3.12.1
```

Update `requirements.txt`:
```
Django==4.2
djangorestframework==3.14.0
djangorestframework-simplejwt==5.5.1
django-cors-headers==4.0.0
django-filter==23.1
gunicorn==21.2.0
whitenoise==6.6.0
mysql-connector-python==8.0.33
dj-database-url==1.3.0
python-dotenv==1.2.1
```

#### Step 2: Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Add PostgreSQL addon (free tier)
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY='your-secret-key-here'
heroku config:set DEBUG='False'
heroku config:set ALLOWED_HOSTS='your-app-name.herokuapp.com'
heroku config:set CORS_ALLOWED_ORIGINS='https://your-frontend-url.com'

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# View logs
heroku logs --tail
```

### Option B: Deploy to Railway.app (Modern Alternative)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Create project
railway init

# Deploy
railway up

# View logs
railway logs
```

### Option C: AWS EC2 + RDS

1. Launch EC2 instance (Ubuntu 22.04 LTS)
2. Create RDS MySQL database
3. Install Python, pip, virtualenv
4. Clone repository and install dependencies
5. Configure Gunicorn and Nginx
6. Set up SSL certificate (Let's Encrypt)
7. Configure domain and DNS

## Phase 2: Frontend Deployment (React)

### Option A: Deploy to Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Navigate to frontend directory
cd frontend

# Deploy
vercel

# Set environment variables in Vercel dashboard
# REACT_APP_API_URL=https://your-backend-url.herokuapp.com
```

### Option B: Deploy to Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Login
netlify login

# Create production build
npm run build

# Deploy
netlify deploy --prod --dir=build

# Or using GitHub integration:
# 1. Push code to GitHub
# 2. Connect repository in Netlify dashboard
# 3. Set build command: npm run build
# 4. Set publish directory: build
```

### Option C: AWS S3 + CloudFront

```bash
# Build React app
npm run build

# Create S3 bucket
aws s3 mb s3://your-bucket-name

# Upload files
aws s3 sync build/ s3://your-bucket-name --delete

# Create CloudFront distribution (from AWS console)
```

## Phase 3: Database Setup

### Production Database Recommendation
Use PostgreSQL (more robust than MySQL):

```bash
# On Heroku (automatic with addon)
# On Railway
railway add postgres

# On AWS
# Create RDS PostgreSQL instance via AWS console
```

### Database Migration

```bash
# Run all migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (if you have fixtures)
python manage.py loaddata initial_data.json
```

## Phase 4: Email Configuration

### Using Gmail (FREE)

1. Enable "Less secure app access":
   - Go to Google Account settings
   - Security tab
   - Allow less secure apps

2. Set environment variables:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Using SendGrid (Production)

1. Create SendGrid account (free tier available)
2. Get API key
3. Set environment variables:
```
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=your-api-key
```

## Phase 5: Security Configuration

### SSL/TLS Certificate (HTTPS)

```bash
# Using Let's Encrypt (free)
sudo apt-get install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

### Security Headers in Django

```python
# settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}
```

### CORS Configuration

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

## Phase 6: Monitoring & Logging

### Error Tracking with Sentry

```bash
# Install Sentry SDK
pip install sentry-sdk

# Add to Django settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

### Application Performance Monitoring (APM)

```bash
# Using New Relic
pip install newrelic

# Initialize with Django
newrelic-admin run-program gunicorn library_config.wsgi
```

## Phase 7: Domain Setup

1. Register domain (Namecheap, GoDaddy, etc.)
2. Point DNS to your hosting provider
3. Update ALLOWED_HOSTS with domain name
4. Update CORS_ALLOWED_ORIGINS with domain URL

## Phase 8: CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Heroku
      env:
        HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
      run: |
        git push https://heroku:$HEROKU_API_KEY@git.heroku.com/your-app-name.git main
```

## Deployment Checklist

### Backend
- [ ] Update settings.py for production
- [ ] Set all environment variables
- [ ] Run migrations on production
- [ ] Create superuser
- [ ] Test API endpoints
- [ ] Configure email service
- [ ] Set up error monitoring
- [ ] Configure domain and SSL

### Frontend
- [ ] Build production bundle
- [ ] Set API_URL to production backend
- [ ] Test all API integrations
- [ ] Test authentication flow
- [ ] Configure custom domain
- [ ] Set up CDN/caching

### Database
- [ ] Backup strategy
- [ ] Connection pooling configured
- [ ] Indexes created
- [ ] Monitoring set up

### Monitoring
- [ ] Error tracking (Sentry)
- [ ] Application monitoring (New Relic)
- [ ] Log aggregation (CloudWatch/LogRocket)
- [ ] Uptime monitoring

## Post-Deployment Testing

```bash
# Test backend
curl -X POST https://your-backend.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Test frontend
# Visit https://your-frontend.com and test login/register
```

## Scaling Considerations

### Horizontal Scaling
- Multiple server instances
- Load balancer (AWS ELB, Nginx)
- Database replication

### Vertical Scaling
- Upgrade server resources
- Optimize database queries
- Implement caching (Redis)

### Database Optimization
- Add indexes
- Archive old data
- Connection pooling

## Disaster Recovery

### Backup Strategy
```bash
# Database backup (daily)
heroku pg:backups:capture

# Code repository (GitHub)
# Regular commits and backups
```

### Restore Process
```bash
# From Heroku backup
heroku pg:backups:restore a506

# From GitHub
git clone <repository>
```

## Cost Estimation (Monthly)

| Service | Cost | Notes |
|---------|------|-------|
| Heroku | $7-50 | Depends on dyno size |
| Vercel | Free-$20 | Free tier available |
| Database | $9-100+ | Depends on size |
| Email | Free-50 | SendGrid free tier: 100/day |
| **Total** | **$16-170+** | Can be kept under $20/month |

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check application logs
   - Verify database connection
   - Check memory usage

2. **CORS Errors**
   - Update CORS_ALLOWED_ORIGINS
   - Check frontend URL configuration
   - Clear browser cache

3. **Static Files Not Loading**
   - Run collectstatic: `python manage.py collectstatic`
   - Check STATIC_URL and STATIC_ROOT

4. **Email Not Sending**
   - Verify email credentials
   - Check email configuration
   - Review logs for errors

## Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [React Production Build](https://create-react-app.dev/docs/production-build/)
- [Heroku Django Guide](https://devcenter.heroku.com/articles/deploying-python)
- [Vercel Documentation](https://vercel.com/docs)

## Support

For deployment issues:
1. Check application logs
2. Review environment variables
3. Verify network connectivity
4. Contact hosting provider support
