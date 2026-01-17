from django.contrib import admin
from .models import Book, IssuedBook, Reservation, Fine, Notification


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'total_copies',
        'available_copies',
        'created_at',
    )
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category', 'created_at')


@admin.register(IssuedBook)
class IssuedBookAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'book',
        'issue_date',
        'due_date',
        'status',
        'fine_amount',
    )
    search_fields = ('user__username', 'book__title')
    list_filter = ('status', 'issue_date')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'book',
        'reserved_at',
        'status',
    )
    search_fields = ('user__username', 'book__title')
    list_filter = ('status', 'reserved_at')


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'amount',
        'reason',
        'paid',
        'created_at',
    )
    search_fields = ('user__username', 'reason')
    list_filter = ('paid', 'created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'notification_type',
        'is_read',
        'created_at',
    )
    search_fields = ('user__username', 'message')
    list_filter = ('notification_type', 'is_read', 'created_at')
