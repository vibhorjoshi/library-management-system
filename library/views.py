from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Book, IssuedBook, Reservation, Fine, Notification
from .serializers import (UserSerializer, BookSerializer, IssuedBookSerializer, 
                          ReservationSerializer, FineSerializer, NotificationSerializer)


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
        
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff
            }, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def current_user(self, request):
        user_id = request.GET.get("user_id")
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                return Response({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_staff": user.is_staff
                }, status=status.HTTP_200_OK)
            except:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "No user ID provided"}, status=status.HTTP_400_BAD_REQUEST)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        search = self.request.query_params.get("search", "")
        if search:
            return Book.objects.filter(title__icontains=search) | \
                   Book.objects.filter(author__icontains=search) | \
                   Book.objects.filter(category__icontains=search)
        return Book.objects.all()
    
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        total_books = Book.objects.count()
        available_books = Book.objects.filter(available_copies__gt=0).count()
        return Response({
            "total_books": total_books,
            "available_books": available_books
        })


class IssuedBookViewSet(viewsets.ModelViewSet):
    queryset = IssuedBook.objects.all()
    serializer_class = IssuedBookSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return IssuedBook.objects.filter(user_id=user_id)
        return IssuedBook.objects.all()
    
    @action(detail=False, methods=["post"])
    def issue_book(self, request):
        book_id = request.data.get("book_id")
        user_id = request.data.get("user_id")
        
        try:
            book = Book.objects.get(id=book_id)
            user = User.objects.get(id=user_id)
            
            if book.available_copies <= 0:
                return Response({"error": "Book not available"}, status=status.HTTP_400_BAD_REQUEST)
            
            issued_book = IssuedBook.objects.create(
                user=user,
                book=book,
                due_date=timezone.now() + timedelta(days=14)
            )
            
            book.available_copies -= 1
            book.save()
            
            return Response(IssuedBookSerializer(issued_book).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        try:
            issued_book = self.get_object()
            
            if issued_book.status != "issued":
                return Response({"error": "Book already returned"}, status=status.HTTP_400_BAD_REQUEST)
            
            issued_book.status = "returned"
            issued_book.return_date = timezone.now()
            issued_book.save()
            
            issued_book.book.available_copies += 1
            issued_book.book.save()
            
            return Response(IssuedBookSerializer(issued_book).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return Reservation.objects.filter(user_id=user_id)
        return Reservation.objects.all()
    
    def create(self, request, *args, **kwargs):
        book_id = request.data.get("book_id")
        user_id = request.data.get("user_id")
        
        try:
            book = Book.objects.get(id=book_id)
            user = User.objects.get(id=user_id)
            
            existing = Reservation.objects.filter(user=user, book=book).first()
            if existing:
                return Response({"error": "Already reserved"}, status=status.HTTP_400_BAD_REQUEST)
            
            reservation = Reservation.objects.create(user=user, book=book)
            return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FineViewSet(viewsets.ModelViewSet):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return Fine.objects.filter(user_id=user_id)
        return Fine.objects.all()
    
    @action(detail=True, methods=["post"])
    def pay_fine(self, request, pk=None):
        try:
            fine = self.get_object()
            fine.paid = True
            fine.paid_at = timezone.now()
            fine.save()
            return Response(FineSerializer(fine).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return Notification.objects.filter(user_id=user_id)
        return Notification.objects.all()
