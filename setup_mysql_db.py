import mysql.connector
from mysql.connector import Error

try:
    print("Connecting to MySQL with root account...")
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pubg@123"
    )
    
    if connection.is_connected():
        print(" Connected to MySQL")
        cursor = connection.cursor()
        
        # Create database
        print("Creating database library_db...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(" Database created")
        
        # Create user
        print("Creating user library_user...")
        cursor.execute("DROP USER IF EXISTS 'library_user'@'localhost'")
        cursor.execute("CREATE USER 'library_user'@'localhost' IDENTIFIED BY 'library_pass123'")
        print(" User created")
        
        # Grant privileges
        print("Granting privileges...")
        cursor.execute("GRANT ALL PRIVILEGES ON library_db.* TO 'library_user'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        print(" Privileges granted")
        
        cursor.close()
        connection.close()
        print("\n MySQL setup complete!")
        
except Error as e:
    print(f" Error: {e}")
