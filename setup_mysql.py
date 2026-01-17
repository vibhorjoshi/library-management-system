import mysql.connector
from mysql.connector import Error

# Try different credential combinations
credentials = [
    {"user": "root", "password": "root", "host": "localhost"},
    {"user": "root", "password": "", "host": "localhost"},
    {"user": "mysql", "password": "", "host": "localhost"},
]

connection = None
for cred in credentials:
    try:
        pwd_display = "*" * len(cred["password"]) if cred["password"] else "(empty)"
        print(f"Trying {cred['user']}:{pwd_display}")
        connection = mysql.connector.connect(
            host=cred["host"],
            user=cred["user"],
            password=cred["password"]
        )
        if connection.is_connected():
            print(f" Connected as {cred['user']}")
            break
    except Error as e:
        print(f" Failed: {str(e)[:50]}")

if connection and connection.is_connected():
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute("CREATE USER IF NOT EXISTS 'library_user'@'localhost' IDENTIFIED BY 'library_pass123'")
    cursor.execute("GRANT ALL PRIVILEGES ON library_db.* TO 'library_user'@'localhost'")
    cursor.execute("FLUSH PRIVILEGES")
    cursor.close()
    connection.close()
    print(" MySQL setup complete!")
else:
    print(" Could not connect to MySQL")
