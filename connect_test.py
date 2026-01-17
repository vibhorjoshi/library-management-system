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
        self.FINE_PER_DAY = 5

    def connect(self):
        """Establish database connection with auto-create DB"""
        try:
            # First, try to create database if it doesn''t exist
            try:
                conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    auth_plugin="mysql_native_password"
                )
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                cursor.close()
                conn.close()
            except:
                pass
            
            # Now connect to the database
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                auth_plugin="mysql_native_password"
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("  Connected to database successfully!")
            return True
        except Error as e:
            print(f"  Connection Error: {e}")
            print(" Make sure MySQL is running and credentials are correct.")
            return False
