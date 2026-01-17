from django.db import models
from django.contrib.auth.models import User
import bcrypt
from django.utils import timezone


class College(models.Model):
    """
    Multi-tenant College/Institution model for SaaS platform.
    Each college is a separate tenant with isolated data.
    """
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    location = models.CharField(max_length=255, blank=True)
    admin_email = models.EmailField()
    subscription_plan = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic - Up to 100 users'),
            ('pro', 'Pro - Up to 1000 users'),
            ('enterprise', 'Enterprise - Unlimited'),
        ],
        default='basic'
    )
    is_active = models.BooleanField(default=True)
    max_users = models.IntegerField(default=100)
    current_users = models.IntegerField(default=0)
    
    # Billing
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    billing_cycle_start = models.DateField(null=True, blank=True)
    billing_cycle_end = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'College'
        verbose_name_plural = 'Colleges'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_subscription_limit(self):
        """Get maximum users allowed for this subscription plan."""
        limits = {
            'basic': 100,
            'pro': 1000,
            'enterprise': 999999,
        }
        return limits.get(self.subscription_plan, self.max_users)
    
    def can_add_user(self):
        """Check if college can add more users based on subscription."""
        return self.current_users < self.get_subscription_limit()


class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('staff', 'Non Teaching Staff'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='users', null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.college.name if self.college else 'No College'})"

    class Meta:
        ordering = ['user']


class Book(models.Model):
    CATEGORY_CHOICES = [
        ("Fiction", "Fiction"),
        ("Non-Fiction", "Non-Fiction"),
        ("Science", "Science"),
        ("History", "History"),
        ("Programming", "Programming"),
        ("Psychology", "Psychology"),
    ]
    
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='books', null=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    published_year = models.IntegerField()
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        unique_together = ('college', 'isbn')  # ISBN unique per college only
    
    def __str__(self):
        return f"{self.title} ({self.college.code if self.college else 'Global'})"


class IssuedBook(models.Model):
    STATUS_CHOICES = [
        ("issued", "Issued"),
        ("returned", "Returned"),
        ("overdue", "Overdue"),
    ]
    
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='issued_books', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="issued")
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ["-issue_date"]
        indexes = [
            models.Index(fields=['college', 'user']),
            models.Index(fields=['college', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.college.code if self.college else 'Global'})"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("fulfilled", "Fulfilled"),
        ("cancelled", "Cancelled"),
    ]
    
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='reservations', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    class Meta:
        unique_together = ("user", "book")
        ordering = ["reserved_at"]
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.college.code if self.college else 'Global'})"


class Fine(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='fines', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issued_book = models.ForeignKey(IssuedBook, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    paid = models.BooleanField(default=False)
    payment_intent_id = models.CharField(max_length=255, null=True, blank=True)  # Stripe
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['college', 'user']),
            models.Index(fields=['college', 'paid']),
        ]
    
    def __str__(self):
        return f"Fine - {self.user.username} - Rs.{self.amount} ({self.college.code if self.college else 'Global'})"


class Notification(models.Model):
    TYPE_CHOICES = [
        ("due_reminder", "Due Reminder"),
        ("overdue", "Overdue"),
        ("reservation", "Reservation Fulfilled"),
        ("fine", "Fine Notice"),
    ]
    
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='notifications', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['college', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type} ({self.college.code if self.college else 'Global'})"
