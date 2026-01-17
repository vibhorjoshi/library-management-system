@echo off
REM Start MySQL if not running
net start MySQL80 >nul 2>&1

REM Wait for MySQL to start
timeout /t 2 /nobreak

REM Create database and user
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u root -pPubg@123 -e "DROP DATABASE IF EXISTS library_db;"
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u root -pPubg@123 -e "CREATE DATABASE library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u root -pPubg@123 -e "DROP USER IF EXISTS 'library_user'@'localhost';"
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u root -pPubg@123 -e "CREATE USER 'library_user'@'localhost' IDENTIFIED BY 'library_pass123';"
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u root -pPubg@123 -e "GRANT ALL PRIVILEGES ON library_db.* TO 'library_user'@'localhost';"
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u root -pPubg@123 -e "FLUSH PRIVILEGES;"
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u root -pPubg@123 -e "SHOW DATABASES;"

echo.
echo MySQL Setup Complete!
pause
