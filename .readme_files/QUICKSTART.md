#  Quick Start Guide

## Step 1: Set Up Environment

### Windows
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Initialize Database

```bash
# Run migrations
python manage.py migrate

# Seed sample data
python seed.py

# Create superuser (if needed)
python manage.py createsuperuser
```

## Step 3: Run the Server

```bash
python manage.py runserver 0.0.0.0:8000
```

## Step 4: Access the Application

- **Frontend**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api

##  Demo Credentials

- **Username**: admin
- **Password**: admin123

##  Features Overview

### Dashboard
- View total books, borrowed books, and pending fines
- Quick statistics at a glance

### Browse Books
- Search books by title or author
- Filter by availability
- Borrow or reserve books

### My Books
- View all borrowed books
- Check due dates
- Return books

### Fines
- View pending fines
- Pay fines online

##  Troubleshooting

### Port 8000 already in use
```bash
python manage.py runserver 0.0.0.0:8001
```

### Database needs reset
```bash
rm db.sqlite3
python manage.py migrate
python seed.py
```

### Missing dependencies
```bash
pip install -r requirements.txt
```

##  Project Structure

```
.
 library/              # Django app
    models.py        # Database models
    views.py         # API endpoints
    serializers.py   # Data serializers
    urls.py          # URL routing
    migrations/      # Database migrations
 library_config/       # Django settings
 templates/
    index.html       # Main frontend
 manage.py
 requirements.txt
 seed.py              # Sample data
 README.md
```

##  Important Files

- `library_config/settings.py` - Django configuration
- `library/models.py` - Database schema
- `library/views.py` - API logic
- `templates/index.html` - Frontend code

---

For detailed API documentation, see README.md
