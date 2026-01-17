from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserViewSet, BookViewSet, IssuedBookViewSet, 
                    ReservationViewSet, FineViewSet, NotificationViewSet)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"books", BookViewSet)
router.register(r"issued-books", IssuedBookViewSet, basename="issued-book")
router.register(r"reservations", ReservationViewSet, basename="reservation")
router.register(r"fines", FineViewSet, basename="fine")
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
]


