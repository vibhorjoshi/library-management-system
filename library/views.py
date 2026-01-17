from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from .models import Book, IssuedBook, Reservation, Fine, Notification, Profile
from .serializers import (UserSerializer, BookSerializer, IssuedBookSerializer, 
                          ReservationSerializer, FineSerializer, NotificationSerializer)
from .decorators import role_required


# ============ AUTHENTICATION VIEWS ============

def login_view(request):
    if request.user.is_authenticated:
        role = request.user.profile.role
        return redirect(f'{role}_dashboard')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            role = user.profile.role
            return redirect(f'{role}_dashboard')
        else:
            return render(request, "auth/login.html", {"error": "Invalid credentials"})

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect('login')


# ============ DASHBOARD VIEWS ============

@role_required('student')
def student_dashboard(request):
    context = {
        'user': request.user,
        'issued_books': IssuedBook.objects.filter(user=request.user),
        'reservations': Reservation.objects.filter(user=request.user),
    }
    return render(request, "dashboards/student.html", context)


@role_required('teacher')
def teacher_dashboard(request):
    context = {
        'user': request.user,
        'total_students': Profile.objects.filter(role='student').count(),
        'total_books': Book.objects.count(),
        'issued_books': IssuedBook.objects.count(),
    }
    return render(request, "dashboards/teacher.html", context)


@role_required('staff')
def staff_dashboard(request):
    context = {
        'user': request.user,
        'total_users': User.objects.count(),
        'total_books': Book.objects.count(),
        'total_fines': Fine.objects.count(),
    }
    return render(request, "dashboards/staff.html", context)


# ============ API VIEWSETS (EXISTING) ============

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


class IssuedBookViewSet(viewsets.ModelViewSet):
    queryset = IssuedBook.objects.all()
    serializer_class = IssuedBookSerializer
    permission_classes = [IsAuthenticated]


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]


class FineViewSet(viewsets.ModelViewSet):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    permission_classes = [IsAuthenticated]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
