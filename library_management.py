import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import getpass
import re
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

class LibraryManagementSystem:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self.current_user = None
        self.user_role = None
        self.FINE_PER_DAY = 5  # Fine in currency units per day

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print(" Connected to database successfully!")
            return True
        except Error as e:
            print(f" Connection Error: {e}")
            return False

    def create_tables(self):
        """Create necessary database tables"""
        queries = [
            """CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                role ENUM('student', 'librarian', 'admin') DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS books (
                book_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(100) NOT NULL,
                isbn VARCHAR(20) UNIQUE,
                category VARCHAR(50),
                total_copies INT DEFAULT 1,
                available_copies INT DEFAULT 1,
                published_year INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS issued_books (
                issue_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                issue_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                due_date DATE,
                return_date DATE,
                status ENUM('issued', 'returned', 'overdue') DEFAULT 'issued',
                fine_amount DECIMAL(10, 2) DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (book_id) REFERENCES books(book_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS reservations (
                reservation_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('pending', 'fulfilled', 'cancelled') DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (book_id) REFERENCES books(book_id)
            )"""
        ]
        
        for query in queries:
            try:
                self.cursor.execute(query)
                self.connection.commit()
            except Error as e:
                print(f"Table creation error: {e}")

    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password, hash_password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hash_password.encode('utf-8'))

    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_username(self, username):
        """Validate username format"""
        return len(username) >= 3 and len(username) <= 50 and username.isalnum()

    def validate_password(self, password):
        """Validate password strength"""
        return len(password) >= 6

    def register_user(self, username, password, email, role='student'):
        """Register a new user with validation"""
        if not self.validate_username(username):
            print(" Username must be 3-50 alphanumeric characters")
            return False
        
        if not self.validate_password(password):
            print(" Password must be at least 6 characters")
            return False
        
        if not self.validate_email(email):
            print(" Invalid email format")
            return False
        
        try:
            password_hash = self.hash_password(password)
            query = "INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (username, password_hash, email, role))
            self.connection.commit()
            print(f" User '{username}' registered successfully!")
            return True
        except Error as e:
            if "Duplicate" in str(e):
                print(" Username already exists")
            else:
                print(f" Registration error: {e}")
            return False

    def login(self, username, password):
        """Login user with secure password verification"""
        try:
            query = "SELECT * FROM users WHERE username = %s"
            self.cursor.execute(query, (username,))
            user = self.cursor.fetchone()
            
            if user and self.verify_password(password, user['password_hash']):
                self.current_user = user['user_id']
                self.user_role = user['role']
                print(f" Welcome {username}! (Role: {user['role']})")
                return True
            else:
                print(" Invalid username or password")
                return False
        except Error as e:
            print(f" Login error: {e}")
            return False

    def check_overdue_books(self):
        """Check and update overdue books for current user"""
        try:
            query = """UPDATE issued_books 
                      SET status = 'overdue' 
                      WHERE user_id = %s AND due_date < CURDATE() AND status = 'issued'"""
            self.cursor.execute(query, (self.current_user,))
            self.connection.commit()
        except Error as e:
            print(f"Error checking overdue: {e}")

    def add_book(self, title, author, isbn, category, copies, year):
        """Add new book to library (Librarian only)"""
        if self.user_role != 'librarian' and self.user_role != 'admin':
            print(" Only librarians can add books")
            return False
        
        if not title or not author or not category:
            print(" Title, author, and category are required")
            return False
        
        if copies < 1:
            print(" Number of copies must be at least 1")
            return False
        
        try:
            query = """INSERT INTO books (title, author, isbn, category, total_copies, available_copies, published_year) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, (title, author, isbn, category, copies, copies, year))
            self.connection.commit()
            print(f" Book '{title}' added successfully!")
            return True
        except Error as e:
            if "Duplicate" in str(e):
                print(" Book with this ISBN already exists")
            else:
                print(f" Error adding book: {e}")
            return False

    def search_books(self, keyword):
        """Search books by title, author, or category"""
        if not keyword or len(keyword.strip()) == 0:
            print(" Please enter a search keyword")
            return []
        
        try:
            query = """SELECT * FROM books WHERE 
                       title LIKE %s OR author LIKE %s OR category LIKE %s"""
            search_term = f"%{keyword}%"
            self.cursor.execute(query, (search_term, search_term, search_term))
            results = self.cursor.fetchall()
            
            if results:
                print(f"\n{'ID':<5} {'Title':<30} {'Author':<20} {'Available':<10}")
                print("-" * 65)
                for book in results:
                    print(f"{book['book_id']:<5} {book['title']:<30} {book['author']:<20} {book['available_copies']:<10}")
                return results
            else:
                print(" No books found")
                return []
        except Error as e:
            print(f" Search error: {e}")
            return []

    def issue_book(self, book_id, days=14):
        """Issue a book to current user (Student only)"""
        if not self.current_user:
            print(" Must be logged in to issue a book")
            return False
        
        if self.user_role != 'student':
            print(" Only students can issue books")
            return False
        
        try:
            # Check if book is available
            self.cursor.execute("SELECT available_copies, book_id FROM books WHERE book_id = %s", (book_id,))
            book = self.cursor.fetchone()
            
            if not book:
                print(" Book not found")
                return False
            
            if book['available_copies'] <= 0:
                print(" Book not available. Would you like to reserve it? (Not yet implemented)")
                return False
            
            # Check if user already has this book issued
            self.cursor.execute("""SELECT * FROM issued_books 
                                  WHERE user_id = %s AND book_id = %s AND status = 'issued'""", 
                              (self.current_user, book_id))
            if self.cursor.fetchone():
                print(" You already have this book issued")
                return False
            
            # Issue the book
            due_date = datetime.now() + timedelta(days=days)
            query = "INSERT INTO issued_books (user_id, book_id, due_date) VALUES (%s, %s, %s)"
            self.cursor.execute(query, (self.current_user, book_id, due_date.date()))
            
            # Update available copies
            self.cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s", (book_id,))
            
            self.connection.commit()
            print(f" Book issued successfully! Due date: {due_date.date()}")
            return True
        except Error as e:
            print(f" Error issuing book: {e}")
            return False

    def return_book(self, issue_id):
        """Return a book and calculate fine if overdue"""
        if not self.current_user:
            print(" Must be logged in to return a book")
            return False
        
        try:
            # Get issue details
            self.cursor.execute("""SELECT issue_id, book_id, due_date, user_id 
                                 FROM issued_books WHERE issue_id = %s""", (issue_id,))
            issue = self.cursor.fetchone()
            
            if not issue:
                print(" Issue not found")
                return False
            
            if issue['user_id'] != self.current_user:
                print(" You can only return your own books")
                return False
            
            # Calculate fine if overdue
            fine_amount = 0
            today = datetime.now().date()
            if today > issue['due_date']:
                overdue_days = (today - issue['due_date']).days
                fine_amount = overdue_days * self.FINE_PER_DAY
                print(f" Book is {overdue_days} day(s) overdue. Fine: {fine_amount}")
            
            # Update issue status
            self.cursor.execute("""UPDATE issued_books 
                                 SET return_date = NOW(), status = 'returned', fine_amount = %s 
                                 WHERE issue_id = %s""", (fine_amount, issue_id))
            
            # Update available copies
            self.cursor.execute("""UPDATE books SET available_copies = available_copies + 1 
                                 WHERE book_id = %s""", (issue['book_id'],))
            
            # Auto-fulfill reservations if book is available
            self.cursor.execute("""SELECT reservation_id, user_id FROM reservations 
                                 WHERE book_id = %s AND status = 'pending' 
                                 ORDER BY reserved_at LIMIT 1""", (issue['book_id'],))
            reservation = self.cursor.fetchone()
            
            if reservation:
                self.cursor.execute("""UPDATE reservations SET status = 'fulfilled' 
                                     WHERE reservation_id = %s""", (reservation['reservation_id'],))
                print(f" Book fulfilled to reservation #{reservation['reservation_id']}")
            
            self.connection.commit()
            print(" Book returned successfully!")
            if fine_amount > 0:
                print(f"  Total fine to be paid: {fine_amount}")
            return True
        except Error as e:
            print(f" Error returning book: {e}")
            return False

    def view_my_books(self):
        """View books issued to current user"""
        if not self.current_user:
            print(" Must be logged in")
            return
        
        self.check_overdue_books()
        
        try:
            query = """SELECT ib.issue_id, b.title, b.author, ib.issue_date, ib.due_date, ib.status, ib.fine_amount
                      FROM issued_books ib
                      JOIN books b ON ib.book_id = b.book_id
                      WHERE ib.user_id = %s"""
            self.cursor.execute(query, (self.current_user,))
            books = self.cursor.fetchall()
            
            if books:
                print(f"\n{'Issue ID':<10} {'Title':<25} {'Due Date':<12} {'Status':<10} {'Fine':<8}")
                print("-" * 70)
                for book in books:
                    fine_str = f"{book['fine_amount']}" if book['fine_amount'] > 0 else "0"
                    print(f"{book['issue_id']:<10} {book['title']:<25} {str(book['due_date']):<12} {book['status']:<10} {fine_str:<8}")
            else:
                print(" No books issued")
        except Error as e:
            print(f" Error: {e}")

    def view_all_books(self):
        """View all books in library"""
        try:
            self.cursor.execute("SELECT * FROM books")
            books = self.cursor.fetchall()
            
            if books:
                print(f"\n{'ID':<5} {'Title':<30} {'Author':<20} {'Available':<12} {'Total':<8}")
                print("-" * 75)
                for book in books:
                    print(f"{book['book_id']:<5} {book['title']:<30} {book['author']:<20} {book['available_copies']:<12} {book['total_copies']:<8}")
            else:
                print(" No books in library")
        except Error as e:
            print(f" Error: {e}")

    def reserve_book(self, book_id):
        """Reserve a book (Student only)"""
        if not self.current_user:
            print(" Must be logged in to reserve a book")
            return False
        
        if self.user_role != 'student':
            print(" Only students can reserve books")
            return False
        
        try:
            # Check if book exists
            self.cursor.execute("SELECT book_id FROM books WHERE book_id = %s", (book_id,))
            if not self.cursor.fetchone():
                print(" Book not found")
                return False
            
            # Check if already reserved
            self.cursor.execute("""SELECT * FROM reservations 
                                 WHERE user_id = %s AND book_id = %s AND status = 'pending'""", 
                              (self.current_user, book_id))
            if self.cursor.fetchone():
                print(" You already have a pending reservation for this book")
                return False
            
            query = "INSERT INTO reservations (user_id, book_id) VALUES (%s, %s)"
            self.cursor.execute(query, (self.current_user, book_id))
            self.connection.commit()
            print(" Book reserved successfully! You'll be notified when it's available.")
            return True
        except Error as e:
            print(f" Error reserving book: {e}")
            return False

    def view_my_fines(self):
        """View outstanding fines for current user"""
        if not self.current_user:
            print(" Must be logged in")
            return
        
        try:
            query = """SELECT ib.issue_id, b.title, ib.due_date, ib.return_date, ib.fine_amount
                      FROM issued_books ib
                      JOIN books b ON ib.book_id = b.book_id
                      WHERE ib.user_id = %s AND ib.fine_amount > 0"""
            self.cursor.execute(query, (self.current_user,))
            fines = self.cursor.fetchall()
            
            if fines:
                total_fine = sum(fine['fine_amount'] for fine in fines)
                print(f"\n{'Issue ID':<10} {'Title':<30} {'Due Date':<12} {'Fine':<8}")
                print("-" * 65)
                for fine in fines:
                    print(f"{fine['issue_id']:<10} {fine['title']:<30} {str(fine['due_date']):<12} {fine['fine_amount']:<8}")
                print("-" * 65)
                print(f"{'Total Outstanding Fine:':<52} {total_fine}")
            else:
                print(" No outstanding fines!")
        except Error as e:
            print(f" Error: {e}")

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print(" Disconnected from database")


def main_menu():
    """Main menu"""
    print("\n" + "="*50)
    print("   STUDENT LIBRARY MANAGEMENT SYSTEM")
    print("="*50)
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    return input("\nChoose an option: ")


def student_menu():
    """Student menu"""
    print("\n--- Student Menu ---")
    print("1. Search Books")
    print("2. View All Books")
    print("3. Issue Book")
    print("4. Return Book")
    print("5. View My Books")
    print("6. Reserve Book")
    print("7. View My Fines")
    print("8. Logout")
    return input("Choose an option: ")


def librarian_menu():
    """Librarian menu"""
    print("\n--- Librarian Menu ---")
    print("1. Add Book")
    print("2. View All Books")
    print("3. Search Books")
    print("4. Logout")
    return input("Choose an option: ")


if __name__ == "__main__":
    # Load environment variables
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "library_db")
    
    lms = LibraryManagementSystem(
        host=host,
        user=user,
        password=password,
        database=database
    )
    
    if lms.connect():
        lms.create_tables()
        
        while True:
            choice = main_menu()
            
            if choice == "1":
                username = input("Enter username: ")
                password_input = getpass.getpass("Enter password: ")
                email = input("Enter email: ")
                lms.register_user(username, password_input, email)
            
            elif choice == "2":
                username = input("Enter username: ")
                password_input = getpass.getpass("Enter password: ")
                if lms.login(username, password_input):
                    
                    while True:
                        if lms.user_role == "student":
                            option = student_menu()
                            
                            if option == "1":
                                keyword = input("Enter title/author/category: ")
                                lms.search_books(keyword)
                            elif option == "2":
                                lms.view_all_books()
                            elif option == "3":
                                lms.view_all_books()
                                try:
                                    book_id = int(input("Enter book ID to issue: "))
                                    lms.issue_book(book_id)
                                except ValueError:
                                    print(" Invalid book ID")
                            elif option == "4":
                                lms.view_my_books()
                                try:
                                    issue_id = int(input("Enter issue ID to return: "))
                                    lms.return_book(issue_id)
                                except ValueError:
                                    print(" Invalid issue ID")
                            elif option == "5":
                                lms.view_my_books()
                            elif option == "6":
                                lms.view_all_books()
                                try:
                                    book_id = int(input("Enter book ID to reserve: "))
                                    lms.reserve_book(book_id)
                                except ValueError:
                                    print(" Invalid book ID")
                            elif option == "7":
                                lms.view_my_fines()
                            elif option == "8":
                                print(" Logged out")
                                break
                        
                        elif lms.user_role == "librarian":
                            option = librarian_menu()
                            
                            if option == "1":
                                title = input("Enter book title: ")
                                author = input("Enter author: ")
                                isbn = input("Enter ISBN (optional): ").strip() or None
                                category = input("Enter category: ")
                                try:
                                    copies = int(input("Enter number of copies: "))
                                    year = int(input("Enter published year: "))
                                    lms.add_book(title, author, isbn, category, copies, year)
                                except ValueError:
                                    print(" Invalid input for copies or year")
                            elif option == "2":
                                lms.view_all_books()
                            elif option == "3":
                                keyword = input("Enter search keyword: ")
                                lms.search_books(keyword)
                            elif option == "4":
                                print(" Logged out")
                                break
            
            elif choice == "3":
                print(" Thank you for using Library Management System!")
                break
        
        lms.disconnect()
    else:
        print("Failed to connect to database")
