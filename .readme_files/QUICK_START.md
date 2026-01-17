# SETUP INSTRUCTIONS - Library Management System
# ============================================

## STEP 1: Install Dependencies
cd c:\Users\acer\library_management_system
pip install -r requirements.txt

## STEP 2: MySQL Setup (Run these commands in MySQL)
# Open Command Prompt and run:
mysql -u root
# Then in MySQL prompt:
CREATE DATABASE library_db;
CREATE USER "library_user"@"localhost" IDENTIFIED BY "library123";
GRANT ALL PRIVILEGES ON library_db.* TO "library_user"@"localhost";
FLUSH PRIVILEGES;
EXIT;

## STEP 3: Update .env file with MySQL credentials:
DB_HOST=localhost
DB_USER=library_user
DB_PASSWORD=library123
DB_NAME=library_db

## STEP 4: Run the application
python library_management.py

## STEP 5: Follow the menu prompts
- Register a new user
- Login with your credentials
- Browse and manage books!
