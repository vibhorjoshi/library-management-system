import subprocess

mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

commands = [
    "CREATE DATABASE IF NOT EXISTS library_db;",
    "CREATE USER IF NOT EXISTS library_user@localhost IDENTIFIED BY library123;",
    "GRANT ALL PRIVILEGES ON library_db.* TO library_user@localhost;",
    "FLUSH PRIVILEGES;"
]

for cmd in commands:
    try:
        process = subprocess.Popen(
            [mysql_path, "-u", "root"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=cmd, timeout=5)
        print(f" Executed: {cmd[:50]}")
        if stderr and "error" in stderr.lower():
            print(f"  Error: {stderr[:100]}")
    except Exception as e:
        print(f" Failed to execute: {str(e)[:100]}")