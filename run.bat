@echo off
cd /d c:\Users\acer\library_management_system
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
