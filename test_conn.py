import mysql.connector
from mysql.connector import Error

# Test connection with auth_plugin
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        auth_plugin="mysql_native_password"
    )
    print("Connection successful!")
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print("Database created!")
    cursor.close()
    conn.close()
except Error as e:
    print(f"Error: {e}")
    # Try without password parameter
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            auth_plugin="mysql_native_password"
        )
        print("Connection successful with no password param!")
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("Database created!")
        cursor.close()
        conn.close()
    except Error as e2:
        print(f"Error 2: {e2}")