import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_config.settings")
django.setup()

from library.models import Book

books_data = [
    {"title": "Python Basics", "author": "John Doe", "isbn": "ISBN-001", "category": "Programming", "published_year": 2023, "total_copies": 5, "available_copies": 5},
    {"title": "Web Development", "author": "Jane Smith", "isbn": "ISBN-002", "category": "Programming", "published_year": 2023, "total_copies": 3, "available_copies": 3},
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "ISBN-003", "category": "Fiction", "published_year": 1925, "total_copies": 2, "available_copies": 2},
    {"title": "Sapiens", "author": "Yuval Noah Harari", "isbn": "ISBN-004", "category": "History", "published_year": 2014, "total_copies": 4, "available_copies": 4},
    {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "isbn": "ISBN-005", "category": "Psychology", "published_year": 2011, "total_copies": 3, "available_copies": 3},
]

for book in books_data:
    if not Book.objects.filter(isbn=book["isbn"]).exists():
        Book.objects.create(**book)
        print(f" {book['title']}")

print(f"\nTotal books: {Book.objects.count()}")
