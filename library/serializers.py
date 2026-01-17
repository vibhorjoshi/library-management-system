from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, IssuedBook, Reservation, Fine, Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "isbn", "category", "published_year", 
                  "total_copies", "available_copies", "created_at")


class IssuedBookSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = IssuedBook
        fields = ("id", "user", "book", "issue_date", "due_date", "return_date", 
                  "status", "fine_amount")


class ReservationSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Reservation
        fields = ("id", "user", "book", "reserved_at", "status")


class FineSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Fine
        fields = ("id", "user", "issued_book", "amount", "reason", "paid", 
                  "created_at", "paid_at")


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ("id", "user", "message", "notification_type", "is_read", "created_at")
