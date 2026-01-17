"""
Multi-tenant API views for college/institution management.

These views implement per-college isolation and provide admin dashboards
for managing multiple tenants in the SaaS platform.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from decimal import Decimal

from .models import College, Profile, Book, IssuedBook, Fine, Reservation
from .college_serializers import (
    CollegeSerializer, CollegeBillingSerializer,
    CollegeStatsSerializer, UserWithCollegeSerializer
)
from .tenant_utils import tenant_required, admin_or_college_admin_required


class CollegeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing colleges/institutions.
    Only superusers can manage colleges.
    """
    
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Admin can see all colleges, others see their own."""
        if self.request.user.is_superuser:
            return College.objects.all()
        
        # Regular users see only their college
        try:
            return College.objects.filter(id=self.request.user.profile.college.id)
        except:
            return College.objects.none()
    
    def perform_create(self, serializer):
        """Create new college."""
        college = serializer.save()
        return college
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get college statistics dashboard."""
        college = self.get_object()
        
        # Check access
        if not request.user.is_superuser:
            if request.user.profile.college != college:
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Calculate statistics
        stats = self._calculate_stats(college)
        
        serializer = CollegeStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get all users in college."""
        college = self.get_object()
        
        # Check access
        if not request.user.is_superuser and request.user.profile.college != college:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        users = Profile.objects.filter(college=college).select_related('user')
        data = [
            {
                'id': p.user.id,
                'username': p.user.username,
                'email': p.user.email,
                'name': f"{p.user.first_name} {p.user.last_name}",
                'role': p.role,
                'created_at': p.created_at,
            }
            for p in users
        ]
        
        return Response({
            'college': college.name,
            'total_users': len(data),
            'users': data
        })
    
    @action(detail=True, methods=['get', 'patch'])
    def billing(self, request, pk=None):
        """Get or update college billing information."""
        college = self.get_object()
        
        # Only superusers and college admins can access
        if not request.user.is_superuser:
            if request.user.profile.college != college:
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if request.method == 'GET':
            serializer = CollegeBillingSerializer(college)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            if not request.user.is_superuser:
                return Response(
                    {'error': 'Only superusers can modify billing'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = CollegeBillingSerializer(
                college,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a college."""
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only superusers can activate colleges'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        college = self.get_object()
        college.is_active = True
        college.save()
        
        return Response({
            'message': f"College {college.name} activated",
            'college': CollegeSerializer(college).data
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a college."""
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only superusers can deactivate colleges'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        college = self.get_object()
        college.is_active = False
        college.save()
        
        return Response({
            'message': f"College {college.name} deactivated",
            'college': CollegeSerializer(college).data
        })
    
    @action(detail=True, methods=['post'])
    def upgrade_plan(self, request, pk=None):
        """Upgrade subscription plan."""
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only superusers can upgrade plans'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        college = self.get_object()
        new_plan = request.data.get('plan')
        
        if new_plan not in ['basic', 'pro', 'enterprise']:
            return Response(
                {'error': 'Invalid plan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        college.subscription_plan = new_plan
        
        # Update monthly fee based on plan
        fees = {
            'basic': Decimal('29.99'),
            'pro': Decimal('99.99'),
            'enterprise': Decimal('299.99'),
        }
        college.monthly_fee = fees.get(new_plan, Decimal('0'))
        
        college.save()
        
        return Response({
            'message': f"College upgraded to {new_plan} plan",
            'college': CollegeSerializer(college).data
        })
    
    def _calculate_stats(self, college):
        """Calculate college statistics."""
        
        # Count users
        total_users = Profile.objects.filter(college=college).count()
        
        # Count books
        total_books = Book.objects.filter(college=college).count()
        
        # Calculate fines
        fines = Fine.objects.filter(college=college)
        total_fines = fines.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        pending_fines = fines.filter(paid=False).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        # Count active issues
        active_issues = IssuedBook.objects.filter(
            college=college,
            status='issued'
        ).count()
        
        # Count overdue books
        overdue_books = IssuedBook.objects.filter(
            college=college,
            status='overdue'
        ).count()
        
        # Count pending reservations
        pending_reservations = Reservation.objects.filter(
            college=college,
            status='pending'
        ).count()
        
        # Calculate subscription usage percentage
        limit = college.get_subscription_limit()
        subscription_usage = (total_users / limit * 100) if limit > 0 else 0
        
        return {
            'total_users': total_users,
            'total_books': total_books,
            'total_fines': total_fines,
            'pending_fines': pending_fines,
            'active_issues': active_issues,
            'overdue_books': overdue_books,
            'pending_reservations': pending_reservations,
            'subscription_usage': subscription_usage,
        }


class TenantAnalyticsView:
    """
    Mixin to add per-college analytics to any viewset.
    Ensures all queries are filtered by college.
    """
    
    def filter_queryset(self, queryset):
        """Override to filter by college."""
        queryset = super().filter_queryset(queryset)
        
        college = self._get_college()
        if college:
            queryset = queryset.filter(college=college)
        
        return queryset
    
    def _get_college(self):
        """Get college from request."""
        if hasattr(self.request, 'college'):
            return self.request.college
        
        try:
            return self.request.user.profile.college
        except:
            return None
    
    def get_serializer_context(self):
        """Add college to serializer context."""
        context = super().get_serializer_context()
        context['college'] = self._get_college()
        return context
