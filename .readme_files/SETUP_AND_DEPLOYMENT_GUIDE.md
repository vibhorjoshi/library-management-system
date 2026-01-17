#  MYSQL SETUP & DEPLOYMENT GUIDE

##  Quick Start

Your Django Library Management System is **RUNNING NOW** at:
- **Frontend**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/

---

##  SETUP WITH MYSQL (Step-by-Step)

### Step 1: Create MySQL Database

Open Command Prompt and run:
```bash
mysql -u root -p
```

Then execute these SQL commands:
```sql
CREATE DATABASE library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library_db;
SHOW TABLES;
EXIT;
```

### Step 2: Configure .env File

Edit `c:\Users\acer\library_management_system\.env`:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=library_db
USE_SQLITE=False
```

### Step 3: Install MySQL Driver

In PowerShell (project directory):
```bash
.\venv\Scripts\Activate.ps1
python -m pip install mysql-connector-python
```

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Admin User

```bash
python manage.py createsuperuser
```

Enter:
- Username: admin
- Email: admin@example.com
- Password: (choose secure password)

### Step 6: Start Server

```bash
python manage.py runserver 0.0.0.0:8000
```

---

##  Add Sample Data

### Via Admin Interface:
1. Go to http://localhost:8000/admin
2. Login with your credentials
3. Click "Books"  "Add Book"
4. Fill in book details and save

### Via Django Shell:
```bash
python manage.py shell

>>> from library.models import Book
>>> Book.objects.create(
...     title="Python Programming",
...     author="John Doe",
...     isbn="978-1234567890",
...     category="Programming",
...     published_year=2023,
...     total_copies=5,
...     available_copies=5
... )
```

---

##  Test the Frontend

1. **Open browser**: http://localhost:8000
2. **Register**: Create new user account
3. **Login**: Use your credentials
4. **Browse Books**: See all available books
5. **Issue Book**: Click "Issue Book" to borrow
6. **View My Books**: Check issued books
7. **Return Book**: Return borrowed book
8. **Check Fines**: View outstanding fines

---

##  Troubleshooting

### MySQL Connection Error
```
Error: Can't connect to MySQL server

Solution:
- Start MySQL: net start MySQL80
- Check credentials in .env
- Verify library_db database exists
```

### Access Denied Error
```
Error: Access denied for user 'root'@'localhost'

Solution:
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED BY 'newpassword';
FLUSH PRIVILEGES;
```

### Module Not Found
```
Error: No module named 'mysql'

Solution:
python -m pip install mysql-connector-python
```

### Tables Not Created
```
Error: relation "library_book" does not exist

Solution:
python manage.py migrate
```

---

##  Database Models

### Book
- title, author, isbn (unique)
- category, published_year
- total_copies, available_copies
- created_at

### IssuedBook
- user (FK to User)
- book (FK to Book)
- issue_date, due_date, return_date
- status (issued/returned/overdue)
- fine_amount

### Fine
- user (FK to User)
- issued_book (FK to IssuedBook)
- amount, reason, paid
- created_at, paid_at

### Reservation
- user (FK to User)
- book (FK to Book)
- reserved_at, status

### Notification
- user (FK to User)
- message, notification_type
- is_read, created_at

---

##  API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/users/register/ | Register user |
| POST | /api/users/login/ | Login |
| GET | /api/books/ | List books |
| GET | /api/books/?search=query | Search |
| POST | /api/issued-books/issue_book/ | Issue book |
| POST | /api/issued-books/{id}/return_book/ | Return book |
| GET | /api/fines/ | View fines |
| POST | /api/fines/{id}/pay_fine/ | Pay fine |

---

##  Backup & Restore MySQL

### Backup Database
```bash
mysqldump -u root -p library_db > backup.sql
```

### Restore Database
```bash
mysql -u root -p library_db < backup.sql
```

---

##  Deployment (Production)

### Using Gunicorn
```bash
python -m pip install gunicorn
gunicorn library_config.wsgi:application --bind 0.0.0.0:8000
```

### Using PostgreSQL (Alternative)
```python
# In settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'library_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Deployment Checklist
- [ ] Set DEBUG = False
- [ ] Update ALLOWED_HOSTS
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Enable HTTPS
- [ ] Configure email backend
- [ ] Set up logging
- [ ] Configure security headers

---

##  Support

For more help:
- Django Docs: https://docs.djangoproject.com
- DRF Docs: https://www.django-rest-framework.org
- MySQL Docs: https://dev.mysql.com/doc/

---

**Project Location**: `c:\Users\acer\library_management_system`
**Main URL**: http://localhost:8000
**Admin URL**: http://localhost:8000/admin
