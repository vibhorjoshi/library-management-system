#  Library Management System

A complete full-stack library management system built with Django REST API backend and vanilla JavaScript frontend.

##  Features

- **User Authentication**: Login and registration system
- **Book Management**: Browse, search, and filter books
- **Book Borrowing**: Issue and return books with due dates
- **Fine Management**: Track and pay fines for overdue books
- **Reservations**: Reserve unavailable books
- **Real-time Dashboard**: View statistics and notifications
- **Responsive Design**: Works on desktop and mobile devices

##  Tech Stack

### Backend
- Django 6.0.1
- Django REST Framework
- SQLite Database
- Python 3.10+

### Frontend
- Vanilla JavaScript (ES6+)
- HTML5
- CSS3 with Flexbox & Grid
- Responsive Design

##  Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment support

##  Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/library_management_system.git
cd library_management_system
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Seed Sample Data
```bash
python seed.py
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Or use demo account: admin / admin123
```

### 7. Run Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### 8. Access the Application
- **Frontend**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API**: http://localhost:8000/api

##  Default Credentials

- **Username**: admin
- **Password**: admin123

##  Project Structure

```
library_management_system/
 library/                    # Django app
    models.py              # Database models
    views.py               # API views
    serializers.py         # DRF serializers
    urls.py                # API routes
    migrations/            # Database migrations
 library_config/            # Django project settings
    settings.py            # Configuration
    urls.py                # URL routing
    wsgi.py                # WSGI configuration
 templates/
    index.html             # Main frontend
 venv/                      # Virtual environment
 manage.py                  # Django management script
 requirements.txt           # Python dependencies
 seed.py                    # Sample data script
```

##  Database Models

### Book
- Title, Author, ISBN
- Category, Published Year
- Total and Available Copies

### IssuedBook
- User, Book relationship
- Issue and Due dates
- Return date, Status, Fine amount

### Reservation
- User, Book relationship
- Status (Pending, Fulfilled, Cancelled)

### Fine
- User, IssuedBook relationship
- Amount, Reason, Payment status

### Notification
- User, Message, Type
- Read/Unread status

##  API Endpoints

### Users
- `POST /api/users/register/` - Register new user
- `POST /api/users/login/` - Login user
- `GET /api/users/current_user/` - Get current user

### Books
- `GET /api/books/` - List all books
- `GET /api/books/{id}/` - Get book details
- `POST /api/books/` - Create book (admin)
- `PUT /api/books/{id}/` - Update book

### Issued Books
- `GET /api/issued-books/` - Get user's issued books
- `POST /api/issued-books/issue_book/` - Borrow book
- `POST /api/issued-books/{id}/return_book/` - Return book

### Fines
- `GET /api/fines/` - Get user's fines
- `POST /api/fines/{id}/pay_fine/` - Mark fine as paid

### Reservations
- `GET /api/reservations/` - Get user's reservations
- `POST /api/reservations/` - Reserve a book
- `DELETE /api/reservations/{id}/` - Cancel reservation

##  Frontend Features

- **Responsive Design**: Mobile-friendly UI
- **Real-time Updates**: Dynamic content loading
- **Search Functionality**: Filter books by title/author
- **Statistics Dashboard**: View key metrics
- **Status Badges**: Visual indicators for book status
- **Error Handling**: User-friendly error messages
- **Loading States**: Visual feedback during operations

##  Authentication

The system uses token-based authentication:
1. User logs in with username/password
2. Server returns user ID as token
3. Token stored in localStorage
4. Used for API requests

##  Responsive Breakpoints

- **Desktop**: 1200px+
- **Tablet**: 768px - 1199px
- **Mobile**: < 768px

##  Deployment

### Production Checklist
- [ ] Set DEBUG = False in settings.py
- [ ] Update ALLOWED_HOSTS
- [ ] Configure proper database (PostgreSQL/MySQL)
- [ ] Set up environment variables
- [ ] Configure HTTPS/SSL
- [ ] Set up static file serving (Nginx/S3)
- [ ] Configure error logging
- [ ] Set up email backend
- [ ] Use Gunicorn/uWSGI as application server

### Deploy to Heroku
```bash
pip install gunicorn
pip freeze > requirements.txt
echo "web: gunicorn library_config.wsgi" > Procfile
git push heroku main
```

##  Troubleshooting

### Port already in use
```bash
# Use different port
python manage.py runserver 0.0.0.0:8001
```

### Database errors
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python seed.py
```

### Static files not loading
```bash
python manage.py collectstatic
```

### API connection errors
- Ensure Django server is running on port 8000
- Check browser console for CORS errors
- Verify API endpoints in JavaScript code

##  Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see LICENSE file for details.

##  Support

For support, email support@librarymanagement.com or open an issue in the repository.

##  Future Enhancements

- [ ] Advanced search filters (by publication year, rating)
- [ ] Book reviews and ratings
- [ ] Email notifications for due dates
- [ ] QR code for books
- [ ] Mobile app (React Native)
- [ ] Payment gateway integration
- [ ] Admin dashboard with analytics
- [ ] Book recommendations engine
- [ ] User profiles and preferences
- [ ] Multi-language support

---

**Made with  by Library Management Team**
