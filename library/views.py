from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db import models
from datetime import timedelta
from .models import Book, IssuedBook, Reservation, Fine, Notification, Profile
from .serializers import (UserSerializer, BookSerializer, IssuedBookSerializer, 
                          ReservationSerializer, FineSerializer, NotificationSerializer)
from .decorators import role_required
from .forms import RegistrationForm


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


def register_view(request):
    """
    Handle user registration with role selection.
    """
    if request.user.is_authenticated:
        role = request.user.profile.role
        return redirect(f'{role}_dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log in after registration
            login(request, user)
            role = user.profile.role
            return redirect(f'{role}_dashboard')
    else:
        form = RegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})


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


# ============ PROTECTED API ENDPOINTS ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_api(request):
    """Get current user's dashboard information."""
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    data = {
        'username': user.username,
        'email': user.email,
        'role': profile.role,
        'full_name': user.get_full_name() or user.username,
        'date_joined': user.date_joined,
    }
    
    # Add role-specific data
    if profile.role == 'student':
        issued_books = IssuedBook.objects.filter(user=user).count()
        reservations = Reservation.objects.filter(user=user).count()
        pending_fines = Fine.objects.filter(user=user, paid=False).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        data.update({
            'issued_books_count': issued_books,
            'reservations_count': reservations,
            'pending_fines': float(pending_fines),
        })
    elif profile.role == 'staff':
        data.update({
            'total_users': User.objects.count(),
            'total_books': Book.objects.count(),
            'total_fines': Fine.objects.aggregate(
                total=models.Sum('amount')
            )['total'] or 0,
            'overdue_books': IssuedBook.objects.filter(
                status='overdue'
            ).count(),
        })
    
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issue_book(request):
    """Issue a book to the current user."""
    user = request.user
    book_id = request.data.get('book_id')
    
    if not book_id:
        return Response(
            {'error': 'book_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response(
            {'error': 'Book not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if book.available_copies <= 0:
        return Response(
            {'error': 'No copies available'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create IssuedBook record
    due_date = timezone.now() + timedelta(days=14)
    issued_book = IssuedBook.objects.create(
        user=user,
        book=book,
        due_date=due_date
    )
    
    # Update available copies
    book.available_copies -= 1
    book.save()
    
    return Response(
        IssuedBookSerializer(issued_book).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def return_book(request):
    """Return an issued book."""
    user = request.user
    issued_book_id = request.data.get('issued_book_id')
    
    if not issued_book_id:
        return Response(
            {'error': 'issued_book_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        issued_book = IssuedBook.objects.get(id=issued_book_id, user=user)
    except IssuedBook.DoesNotExist:
        return Response(
            {'error': 'Issued book not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if issued_book.return_date:
        return Response(
            {'error': 'Book already returned'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Mark as returned
    issued_book.return_date = timezone.now()
    issued_book.status = 'returned'
    issued_book.save()
    
    # Update available copies
    book = issued_book.book
    book.available_copies += 1
    book.save()
    
    return Response(
        IssuedBookSerializer(issued_book).data,
        status=status.HTTP_200_OK
    )


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
