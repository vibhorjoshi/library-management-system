#!/usr/bin/env python3
"""
Library Management System - SQLITE Demo Version
This version uses SQLite for instant testing without MySQL setup
"""
import sqlite3
import bcrypt
from datetime import datetime, timedelta
import re

class DemoLibrarySystem:
    def __init__(self, db_file="library_demo.db"):
        self.db_file = db_file
        self.connection = None
        self.cursor = None
        self.current_user = None
        self.user_role = None
        self.FINE_PER_DAY = 5
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database"""
        self.connection = sqlite3.connect(self.db_file)
        self.cursor = self.connection.cursor()
        self.cursor.row_factory = sqlite3.Row
        self.create_tables()
        print(" SQLite database initialized (demo_library.db)")
    
    def create_tables(self):
        """Create all necessary tables"""
        tables = [
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT "student",
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                category TEXT,
                total_copies INTEGER DEFAULT 1,
                available_copies INTEGER DEFAULT 1,
                published_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS issued_books (
                issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date DATE,
                return_date DATE,
                status TEXT DEFAULT "issued",
                fine_amount INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (book_id) REFERENCES books(book_id)
            )""",
        ]
        for table in tables:
            self.cursor.execute(table)
        self.connection.commit()
    
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    @staticmethod
    def verify_password(password, hash_password):
        return bcrypt.checkpw(password.encode("utf-8"), hash_password.encode("utf-8"))
    
    def register_user(self, username, password, email, role="student"):
        """Register a new user"""
        try:
            password_hash = self.hash_password(password)
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                (username, password_hash, email, role)
            )
            self.connection.commit()
            print(f" User '{username}' registered successfully!")
            return True
        except Exception as e:
            print(f" Registration error: {e}")
            return False
    
    def login(self, username, password):
        """Login user"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = self.cursor.fetchone()
            
            if user and self.verify_password(password, user["password_hash"]):
                self.current_user = user["user_id"]
                self.user_role = user["role"]
                print(f" Welcome {username}! (Role: {user['role']})")
                return True
            else:
                print(" Invalid username or password")
                return False
        except Exception as e:
            print(f" Login error: {e}")
            return False
    
    def add_book(self, title, author, isbn, category, copies, year):
        """Add a new book"""
        try:
            self.cursor.execute(
                "INSERT INTO books (title, author, isbn, category, total_copies, available_copies, published_year) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title, author, isbn, category, copies, copies, year)
            )
            self.connection.commit()
            print(f" Book '{title}' added successfully!")
            return True
        except Exception as e:
            print(f" Error adding book: {e}")
            return False
    
    def view_all_books(self):
        """View all books"""
        self.cursor.execute("SELECT * FROM books")
        books = self.cursor.fetchall()
        
        if books:
            print(f"\n{'ID':<5} {'Title':<30} {'Author':<20} {'Available':<12}")
            print("-" * 67)
            for book in books:
                print(f"{book['book_id']:<5} {book['title']:<30} {book['author']:<20} {book['available_copies']:<12}")
        else:
            print(" No books in library")
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print(" Disconnected from database")


# Demo usage
if __name__ == "__main__":
    lms = DemoLibrarySystem()
    
    print("\n" + "="*50)
    print("  LIBRARY MANAGEMENT SYSTEM - DEMO")
    print("="*50)
    
    # Register test users
    print("\n[Registering test users...]")
    lms.register_user("student1", "pass123", "student@example.com", "student")
    lms.register_user("admin1", "admin123", "admin@example.com", "admin")
    
    # Add test books
    print("\n[Adding sample books...]")
    lms.add_book("Python Programming", "John Doe", "ISBN001", "Programming", 3, 2023)
    lms.add_book("Data Science", "Jane Smith", "ISBN002", "Science", 2, 2022)
    lms.add_book("Web Development", "Bob Johnson", "ISBN003", "Technology", 4, 2023)
    
    # Login and view
    print("\n[Logging in as student1...]")
    lms.login("student1", "pass123")
    
    print("\n[Available books:]")
    lms.view_all_books()
    
    lms.close()
    
    print("\n Demo completed successfully!")
    print("\n  To use the full MySQL version:")
    print("  1. Configure MySQL credentials in .env")
    print("  2. Run: python library_management.py")
