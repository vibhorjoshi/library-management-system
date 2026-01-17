#  QUICK REFERENCE CARD

##  URLS & CREDENTIALS

| Purpose | URL | Username | Password |
|---------|-----|----------|----------|
| Main App | http://localhost:8000 | - | - |
| Admin | http://localhost:8000/admin | admin | admin123 |
| API | http://localhost:8000/api/ | - | - |

##  COMMON TASKS

### Start Development Server
\\\
.\venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
\\\

### Create Superuser
\\\
python manage.py createsuperuser
\\\

### Add Sample Data
1. Go to http://localhost:8000/admin
2. Login with admin/admin123
3. Click "Books" and "Add Book"
4. Fill in details and save

### Test User Registration
1. Go to http://localhost:8000
2. Click "Register"
3. Create test account
4. Click "Login" to test

### Access Django Shell
\\\
python manage.py shell
\\\

##  DATABASE MODELS

- **Book**: title, author, isbn, category, available_copies
- **IssuedBook**: user, book, issue_date, due_date, status
- **Fine**: user, amount, reason, paid
- **Reservation**: user, book, status
- **Notification**: user, message, type

##  ROLE-BASED ACCESS

- **Student/User**: Can issue, return books, pay fines
- **Librarian**: Can add books, manage catalog
- **Admin**: Full access to all features

##  PROJECT STRUCTURE

`
 library_management_system/
  library/              Django App
  library_config/       Django Config
  templates/            Frontend
  static/               CSS, JS, Images
  media/                Uploads
  venv/                 Virtual Env
 manage.py                Main Script
 requirements.txt         Dependencies
`

##  SECURITY FEATURES

 Password hashing (Django built-in)
 Session authentication
 CSRF protection
 SQL injection prevention
 CORS support
 Input validation

##  TO SWITCH TO MYSQL

1. Edit .env:
   USE_SQLITE=False
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=library_db

2. Run migrations:
   python manage.py migrate

##  API ENDPOINTS

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/users/register/ | Register |
| POST | /api/users/login/ | Login |
| GET | /api/books/ | List books |
| GET | /api/books/?search=query | Search |
| POST | /api/issued-books/issue_book/ | Issue book |
| POST | /api/issued-books/{id}/return_book/ | Return book |
| GET | /api/fines/ | View fines |
| POST | /api/fines/{id}/pay_fine/ | Pay fine |

##  VERIFICATION CHECKLIST

- [ ] Server running at http://localhost:8000
- [ ] Admin accessible at http://localhost:8000/admin
- [ ] Can register new user
- [ ] Can login with credentials
- [ ] Can browse books
- [ ] Can issue a book
- [ ] Can return a book
- [ ] Can view fines

