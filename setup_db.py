import mysql.connector
from mysql.connector import Error

# Try different password combinations
passwords_to_try = ["", "root", "password", "mysql"]

for pwd in passwords_to_try:
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=pwd,
            auth_plugin="mysql_native_password"
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("Database created successfully!")
        print(f"Working password: {pwd if pwd else '(empty)'}")
        # Update .env
        with open(".env", "w") as f:
            f.write(f"DB_HOST=localhost\nDB_USER=root\nDB_PASSWORD={pwd}\nDB_NAME=library_db\n")
        cursor.close()
        conn.close()
        break
    except Error as e:
        continue
else:
    print("Could not connect to MySQL")