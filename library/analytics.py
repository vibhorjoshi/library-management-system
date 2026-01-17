"""
Analytics Module for Library Management System
Provides fine statistics, payment trends, and overdue book analytics
"""

from django.db.models import Sum, Count, Q, Avg, Max, Min, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from datetime import timedelta, datetime
from .models import Fine, IssuedBook, User, Book


class AnalyticsError(Exception):
    """Custom exception for analytics errors"""
    pass


# ============================================================================
# FINE STATISTICS
# ============================================================================

def get_fine_statistics(user=None, days=30):
    """
    Get fine statistics (total, paid, unpaid, average).
    
    Args:
        user: Optional User instance (all users if None)
        days: Number of days to look back (default 30)
    
    Returns:
        Dict with fine statistics
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Build query
        query = Fine.objects.filter(created_at__gte=cutoff_date)
        if user:
            query = query.filter(user=user)
        
        # Aggregate statistics
        stats = query.aggregate(
            total_fines=Count('id'),
            total_amount=Sum('amount', output_field=None) or Decimal('0'),
            paid_amount=Sum('amount', filter=Q(paid=True), output_field=None) or Decimal('0'),
            pending_amount=Sum('amount', filter=Q(paid=False), output_field=None) or Decimal('0'),
            avg_fine_amount=Avg('amount', output_field=None) or Decimal('0'),
            max_fine_amount=Max('amount', output_field=None) or Decimal('0'),
            min_fine_amount=Min('amount', output_field=None) or Decimal('0'),
            paid_count=Count('id', filter=Q(paid=True)),
            unpaid_count=Count('id', filter=Q(paid=False)),
        )
        
        # Calculate percentages
        total = stats['total_fines']
        if total > 0:
            stats['paid_percentage'] = round((stats['paid_count'] / total) * 100, 2)
            stats['unpaid_percentage'] = round((stats['unpaid_count'] / total) * 100, 2)
        else:
            stats['paid_percentage'] = 0
            stats['unpaid_percentage'] = 0
        
        # Convert to float for JSON
        for key in ['total_amount', 'paid_amount', 'pending_amount', 'avg_fine_amount', 
                    'max_fine_amount', 'min_fine_amount']:
            stats[key] = float(stats[key]) if stats[key] else 0.0
        
        return stats
    
    except Exception as e:
        raise AnalyticsError(f"Failed to calculate fine statistics: {str(e)}")


def get_payment_trends(days=30, group_by='date'):
    """
    Get payment trends over time.
    
    Args:
        days: Number of days to look back
        group_by: 'date' (daily) or 'week' (weekly)
    
    Returns:
        List of trend data with dates and payment amounts
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get paid fines grouped by date
        trends = Fine.objects.filter(
            paid=True,
            created_at__gte=cutoff_date
        ).annotate(
            payment_date=TruncDate('created_at')
        ).values('payment_date').annotate(
            amount=Sum('amount'),
            count=Count('id')
        ).order_by('payment_date')
        
        # Convert to list of dicts for JSON
        result = [
            {
                'date': trend['payment_date'].isoformat(),
                'amount': float(trend['amount']),
                'count': trend['count']
            }
            for trend in trends
        ]
        
        return result
    
    except Exception as e:
        raise AnalyticsError(f"Failed to calculate payment trends: {str(e)}")


# ============================================================================
# BOOK ANALYTICS
# ============================================================================

def get_overdue_books_analytics():
    """
    Get statistics on overdue books.
    
    Returns:
        Dict with overdue book statistics
    """
    try:
        now = timezone.now()
        
        # Get overdue books
        overdue = IssuedBook.objects.filter(
            return_date__isnull=True,
            due_date__lt=now.date()
        )
        
        stats = {
            'total_overdue': overdue.count(),
            'books_by_days_overdue': {
                '1-7_days': overdue.filter(
                    due_date__gte=(now.date() - timedelta(days=7))
                ).count(),
                '8-14_days': overdue.filter(
                    due_date__gte=(now.date() - timedelta(days=14)),
                    due_date__lt=(now.date() - timedelta(days=7))
                ).count(),
                '15-30_days': overdue.filter(
                    due_date__gte=(now.date() - timedelta(days=30)),
                    due_date__lt=(now.date() - timedelta(days=14))
                ).count(),
                'over_30_days': overdue.filter(
                    due_date__lt=(now.date() - timedelta(days=30))
                ).count(),
            },
            'overdue_users': overdue.values('user').distinct().count(),
            'total_overdue_fine': float(
                Fine.objects.filter(issued_book__in=overdue).aggregate(
                    total=Sum('amount', output_field=None) or Decimal('0')
                )['total'] or Decimal('0')
            ),
        }
        
        return stats
    
    except Exception as e:
        raise AnalyticsError(f"Failed to calculate overdue analytics: {str(e)}")


# ============================================================================
# USER ANALYTICS
# ============================================================================

def get_top_defaulters(limit=10):
    """
    Get users with most unpaid fines.
    
    Args:
        limit: Number of users to return
    
    Returns:
        List of users with fine statistics
    """
    try:
        defaulters = User.objects.annotate(
            unpaid_fines=Count('fine', filter=Q(fine__paid=False)),
            unpaid_amount=Sum('fine__amount', filter=Q(fine__paid=False), output_field=None) or Decimal('0')
        ).filter(unpaid_fines__gt=0).order_by('-unpaid_amount')[:limit]
        
        result = [
            {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'unpaid_fines': user.unpaid_fines,
                'unpaid_amount': float(user.unpaid_amount)
            }
            for user in defaulters
        ]
        
        return result
    
    except Exception as e:
        raise AnalyticsError(f"Failed to get top defaulters: {str(e)}")


def get_top_books(limit=10):
    """
    Get most frequently issued books.
    
    Args:
        limit: Number of books to return
    
    Returns:
        List of books with issue statistics
    """
    try:
        books = Book.objects.annotate(
            times_issued=Count('issuedbook'),
            currently_issued=Count('issuedbook', filter=Q(issuedbook__return_date__isnull=True)),
            currently_overdue=Count('issuedbook', filter=Q(
                issuedbook__return_date__isnull=True,
                issuedbook__due_date__lt=timezone.now().date()
            ))
        ).order_by('-times_issued')[:limit]
        
        result = [
            {
                'book_id': book.id,
                'title': book.title,
                'author': book.author,
                'times_issued': book.times_issued,
                'currently_issued': book.currently_issued,
                'currently_overdue': book.currently_overdue
            }
            for book in books
        ]
        
        return result
    
    except Exception as e:
        raise AnalyticsError(f"Failed to get top books: {str(e)}")


# ============================================================================
# REVENUE ANALYTICS
# ============================================================================

def get_revenue_analytics(days=30):
    """
    Get revenue statistics from fine payments.
    
    Args:
        days: Number of days to look back
    
    Returns:
        Dict with revenue statistics
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        paid_fines = Fine.objects.filter(
            paid=True,
            created_at__gte=cutoff_date
        )
        
        stats = {
            'period_days': days,
            'total_revenue': float(
                paid_fines.aggregate(total=Sum('amount', output_field=None) or Decimal('0'))['total']
            ),
            'total_transactions': paid_fines.count(),
            'avg_transaction': float(
                paid_fines.aggregate(avg=Avg('amount', output_field=None) or Decimal('0'))['avg']
            ),
            'daily_average': 0,
        }
        
        if days > 0:
            stats['daily_average'] = round(stats['total_revenue'] / days, 2)
        
        return stats
    
    except Exception as e:
        raise AnalyticsError(f"Failed to calculate revenue analytics: {str(e)}")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_analytics(request):
    """
    Get personalized analytics for the authenticated user.
    
    Returns fine statistics, payment history, and overdue books.
    """
    try:
        user = request.user
        
        # Get user's fine statistics
        fine_stats = get_fine_statistics(user=user)
        
        # Get user's overdue books
        overdue_books = IssuedBook.objects.filter(
            user=user,
            return_date__isnull=True,
            due_date__lt=timezone.now().date()
        ).count()
        
        # Get user's pending fines
        pending_fines = Fine.objects.filter(
            user=user,
            paid=False
        ).values('id', 'amount', 'created_at', 'issued_book__book__title')
        
        return Response(
            {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'fine_statistics': fine_stats,
                'overdue_books': overdue_books,
                'pending_fines': list(pending_fines),
                'status': 'success'
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'error': str(e), 'status': 'error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_system_analytics(request):
    """
    Get system-wide analytics (admin only).
    
    Returns overall fine statistics, payment trends, and book analytics.
    """
    try:
        days = int(request.query_params.get('days', 30))
        
        # Calculate all analytics
        fine_stats = get_fine_statistics(days=days)
        payment_trends = get_payment_trends(days=days)
        overdue_analytics = get_overdue_books_analytics()
        revenue_stats = get_revenue_analytics(days=days)
        top_defaulters = get_top_defaulters(limit=10)
        top_books = get_top_books(limit=10)
        
        return Response(
            {
                'period_days': days,
                'generated_at': timezone.now().isoformat(),
                'fine_statistics': fine_stats,
                'payment_trends': payment_trends,
                'overdue_analytics': overdue_analytics,
                'revenue_analytics': revenue_stats,
                'top_defaulters': top_defaulters,
                'top_books': top_books,
                'status': 'success'
            },
            status=status.HTTP_200_OK
        )
    
    except ValueError:
        return Response(
            {'error': 'Invalid days parameter', 'status': 'validation_error'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e), 'status': 'error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_fine_statistics_api(request):
    """
    Get fine statistics (admin endpoint).
    
    Query parameters:
    - days: Number of days to look back (default 30)
    
    Returns detailed fine statistics.
    """
    try:
        days = int(request.query_params.get('days', 30))
        stats = get_fine_statistics(days=days)
        
        return Response(
            {
                'period_days': days,
                'statistics': stats,
                'status': 'success'
            },
            status=status.HTTP_200_OK
        )
    
    except ValueError:
        return Response(
            {'error': 'Invalid days parameter', 'status': 'validation_error'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e), 'status': 'error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_payment_trends_api(request):
    """
    Get payment trends over time (admin endpoint).
    
    Query parameters:
    - days: Number of days to look back (default 30)
    
    Returns payment trends grouped by date.
    """
    try:
        days = int(request.query_params.get('days', 30))
        trends = get_payment_trends(days=days)
        
        return Response(
            {
                'period_days': days,
                'trends': trends,
                'status': 'success'
            },
            status=status.HTTP_200_OK
        )
    
    except ValueError:
        return Response(
            {'error': 'Invalid days parameter', 'status': 'validation_error'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e), 'status': 'error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_overdue_analytics_api(request):
    """
    Get overdue books analytics (admin endpoint).
    
    Returns detailed overdue book statistics.
    """
    try:
        analytics = get_overdue_books_analytics()
        
        return Response(
            {
                'analytics': analytics,
                'generated_at': timezone.now().isoformat(),
                'status': 'success'
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'error': str(e), 'status': 'error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_revenue_analytics_api(request):
    """
    Get revenue analytics (admin endpoint).
    
    Query parameters:
    - days: Number of days to look back (default 30)
    
    Returns revenue statistics.
    """
    try:
        days = int(request.query_params.get('days', 30))
        revenue = get_revenue_analytics(days=days)
        
        return Response(
            {
                'revenue': revenue,
                'generated_at': timezone.now().isoformat(),
                'status': 'success'
            },
            status=status.HTTP_200_OK
        )
    
    except ValueError:
        return Response(
            {'error': 'Invalid days parameter', 'status': 'validation_error'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e), 'status': 'error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
