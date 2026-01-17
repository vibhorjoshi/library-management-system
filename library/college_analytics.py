"""
Per-college analytics views for multi-tenant SaaS.

Provides college-specific analytics, reports, and dashboards
for administrators to manage their institution.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import College, Profile, Book, IssuedBook, Fine, Reservation
from .tenant_utils import tenant_required


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@tenant_required
def college_dashboard(request):
    """
    Get college admin dashboard with key metrics.
    Only accessible to users in a college.
    """
    college = request.college
    
    if not college:
        return Response({'error': 'Not assigned to college'}, status=403)
    
    # Verify user belongs to college
    if request.user.profile.college != college:
        return Response({'error': 'Access denied'}, status=403)
    
    # Basic metrics
    total_users = Profile.objects.filter(college=college).count()
    total_books = Book.objects.filter(college=college).count()
    
    # Fine metrics
    fines_data = Fine.objects.filter(college=college)
    total_fines = fines_data.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    paid_fines = fines_data.filter(paid=True).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    pending_fines = total_fines - paid_fines if total_fines else Decimal('0')
    
    # Book metrics
    issued_data = IssuedBook.objects.filter(college=college)
    active_issues = issued_data.filter(status='issued').count()
    overdue_count = issued_data.filter(status='overdue').count()
    
    # Reservation metrics
    pending_reservations = Reservation.objects.filter(
        college=college,
        status='pending'
    ).count()
    
    # Subscription metrics
    usage_percent = (total_users / college.get_subscription_limit() * 100)
    
    return Response({
        'college': {
            'id': college.id,
            'name': college.name,
            'code': college.code,
            'plan': college.subscription_plan,
            'is_active': college.is_active,
        },
        'users': {
            'total': total_users,
            'limit': college.get_subscription_limit(),
            'usage_percent': usage_percent,
        },
        'books': {
            'total': total_books,
            'active_issues': active_issues,
            'overdue': overdue_count,
        },
        'fines': {
            'total_amount': str(total_fines),
            'paid_amount': str(paid_fines),
            'pending_amount': str(pending_fines),
            'paid_percentage': float((paid_fines / total_fines * 100) if total_fines else 0),
        },
        'reservations': {
            'pending': pending_reservations,
        },
        'billing': {
            'plan': college.subscription_plan,
            'monthly_fee': str(college.monthly_fee),
            'billing_cycle_start': college.billing_cycle_start,
            'billing_cycle_end': college.billing_cycle_end,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@tenant_required
def college_fine_analytics(request):
    """Get detailed fine analytics for college."""
    college = request.college
    
    if request.user.profile.college != college:
        return Response({'error': 'Access denied'}, status=403)
    
    # Fine statistics
    fines = Fine.objects.filter(college=college)
    
    # Group by status
    total_fines = fines.count()
    paid_fines = fines.filter(paid=True).count()
    unpaid_fines = fines.filter(paid=False).count()
    
    # Amount statistics
    total_amount = fines.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    paid_amount = fines.filter(paid=True).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    unpaid_amount = total_amount - paid_amount
    
    # Average fine
    avg_fine = fines.aggregate(Avg('amount'))['amount__avg'] or Decimal('0')
    
    # Top defaulters
    defaulters = Profile.objects.filter(college=college).annotate(
        total_unpaid=Sum(
            'user__fine__amount',
            filter=Q(user__fine__paid=False, user__fine__college=college)
        ),
        unpaid_count=Count(
            'user__fine',
            filter=Q(user__fine__paid=False, user__fine__college=college)
        )
    ).filter(unpaid_count__gt=0).order_by('-total_unpaid')[:10]
    
    return Response({
        'summary': {
            'total_fines': total_fines,
            'paid_fines': paid_fines,
            'unpaid_fines': unpaid_fines,
            'total_amount': str(total_amount),
            'paid_amount': str(paid_amount),
            'unpaid_amount': str(unpaid_amount),
            'average_fine': str(avg_fine),
        },
        'top_defaulters': [
            {
                'user_id': p.user.id,
                'username': p.user.username,
                'name': f"{p.user.first_name} {p.user.last_name}",
                'total_unpaid': str(p.total_unpaid or 0),
                'unpaid_count': p.unpaid_count or 0,
            }
            for p in defaulters
        ]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@tenant_required
def college_book_analytics(request):
    """Get detailed book analytics for college."""
    college = request.college
    
    if request.user.profile.college != college:
        return Response({'error': 'Access denied'}, status=403)
    
    # Book statistics
    books = Book.objects.filter(college=college)
    
    total_books = books.count()
    total_copies = books.aggregate(Sum('total_copies'))['total_copies__sum'] or 0
    available_copies = books.aggregate(Sum('available_copies'))['available_copies__sum'] or 0
    issued_copies = total_copies - available_copies
    
    # Most issued books
    most_issued = IssuedBook.objects.filter(college=college).values(
        'book__id', 'book__title', 'book__author'
    ).annotate(
        issue_count=Count('id')
    ).order_by('-issue_count')[:10]
    
    # Category breakdown
    category_breakdown = books.values('category').annotate(
        count=Count('id'),
        copies=Sum('total_copies')
    )
    
    return Response({
        'summary': {
            'total_books': total_books,
            'total_copies': total_copies,
            'available_copies': available_copies,
            'issued_copies': issued_copies,
            'availability_percent': float((available_copies / total_copies * 100) if total_copies else 0),
        },
        'most_issued': [
            {
                'book_id': item['book__id'],
                'title': item['book__title'],
                'author': item['book__author'],
                'times_issued': item['issue_count'],
            }
            for item in most_issued
        ],
        'category_breakdown': list(category_breakdown)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@tenant_required
def college_user_analytics(request):
    """Get detailed user analytics for college."""
    college = request.college
    
    if request.user.profile.college != college:
        return Response({'error': 'Access denied'}, status=403)
    
    profiles = Profile.objects.filter(college=college)
    
    # User statistics
    total_users = profiles.count()
    by_role = profiles.values('role').annotate(count=Count('id'))
    
    # Active users (issued books or fines)
    active_users = profiles.filter(
        Q(user__issuedbook__college=college) |
        Q(user__fine__college=college)
    ).distinct().count()
    
    # Inactive users
    inactive_users = total_users - active_users
    
    # Users with overdue books
    overdue_users = Profile.objects.filter(
        college=college,
        user__issuedbook__status='overdue'
    ).distinct().count()
    
    # Users with pending fines
    fine_users = Profile.objects.filter(
        college=college,
        user__fine__paid=False
    ).distinct().count()
    
    return Response({
        'summary': {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'users_with_overdue_books': overdue_users,
            'users_with_pending_fines': fine_users,
        },
        'by_role': list(by_role)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@tenant_required
def college_billing_report(request):
    """Get college billing report."""
    college = request.college
    
    # Only superusers can view billing reports for all colleges
    if not request.user.is_superuser:
        if request.user.profile.college != college:
            return Response({'error': 'Access denied'}, status=403)
    
    total_users = Profile.objects.filter(college=college).count()
    monthly_fee = college.monthly_fee
    
    # Calculate pro-rata for current billing cycle
    if college.billing_cycle_start and college.billing_cycle_end:
        total_days = (college.billing_cycle_end - college.billing_cycle_start).days
        days_elapsed = (timezone.now().date() - college.billing_cycle_start).days
        pro_rata_amount = monthly_fee * Decimal(days_elapsed) / Decimal(max(total_days, 1))
    else:
        pro_rata_amount = monthly_fee
    
    return Response({
        'college': {
            'id': college.id,
            'name': college.name,
            'code': college.code,
        },
        'subscription': {
            'plan': college.subscription_plan,
            'users': total_users,
            'limit': college.get_subscription_limit(),
            'status': 'active' if college.is_active else 'inactive',
        },
        'billing': {
            'monthly_fee': str(monthly_fee),
            'billing_cycle_start': college.billing_cycle_start,
            'billing_cycle_end': college.billing_cycle_end,
            'pro_rata_amount': str(pro_rata_amount),
            'payment_method': college.payment_method or 'Not configured',
        }
    })
