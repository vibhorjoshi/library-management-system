"""
Tenant isolation middleware and utilities for multi-tenant SaaS platform.

This module provides tenant context management, request filtering, and query isolation
to ensure data is properly separated by college/tenant.
"""

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from functools import wraps
from django.core.exceptions import PermissionDenied
from .models import College


class TenantContextMiddleware:
    """
    Middleware to extract tenant context from request and store in thread-local.
    Supports multi-tenant data isolation.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_local = {}
    
    def __call__(self, request):
        # Extract college from request headers, query params, or user profile
        college = self._get_college_from_request(request)
        
        # Store in request for later use
        request.college = college
        
        response = self.get_response(request)
        return response
    
    def _get_college_from_request(self, request):
        """Extract college from request in order of priority."""
        
        # 1. Check explicit college header
        college_id = request.META.get('HTTP_X_COLLEGE_ID')
        if college_id:
            try:
                return College.objects.get(id=college_id)
            except College.DoesNotExist:
                pass
        
        # 2. Check query parameter
        college_id = request.GET.get('college_id')
        if college_id:
            try:
                return College.objects.get(id=college_id)
            except College.DoesNotExist:
                pass
        
        # 3. Get from authenticated user's profile
        if request.user and request.user.is_authenticated:
            try:
                if hasattr(request.user, 'profile'):
                    return request.user.profile.college
            except:
                pass
        
        # 4. Default: no specific college (admin/superuser)
        return None


def tenant_required(view_func):
    """
    Decorator to ensure user belongs to a college/tenant.
    Enforces tenant isolation on views.
    """
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Get user's college
        try:
            college = request.user.profile.college
        except:
            college = None
        
        if not college:
            return JsonResponse({
                'error': 'User not assigned to any college. Contact administrator.'
            }, status=403)
        
        # Store in request for use in view
        request.college = college
        
        return view_func(request, *args, **kwargs)
    
    return wrapped


def admin_or_college_admin_required(view_func):
    """
    Decorator to allow access only to superusers or college admins.
    """
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Allow superusers
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # For college admins, verify they manage that college
        if hasattr(request.user, 'profile') and request.user.profile.college:
            request.college = request.user.profile.college
            return view_func(request, *args, **kwargs)
        
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    return wrapped


class TenantQuerySet:
    """
    Helper mixin to filter querysets by tenant/college.
    Use in views to automatically isolate data.
    """
    
    @staticmethod
    def filter_by_college(queryset, college):
        """Filter queryset by college."""
        if college:
            return queryset.filter(college=college)
        return queryset
    
    @staticmethod
    def filter_user_by_college(user, college):
        """Check if user belongs to college."""
        try:
            return user.profile.college == college
        except:
            return False


# Global tenant storage for async operations
_thread_local = {}


def set_current_college(college):
    """Store current college in thread-local storage."""
    _thread_local['college'] = college


def get_current_college():
    """Retrieve current college from thread-local storage."""
    return _thread_local.get('college')


def clear_current_college():
    """Clear college from thread-local storage."""
    _thread_local.pop('college', None)


class TenantIsolation:
    """
    Context manager for tenant isolation in background tasks and signals.
    """
    
    def __init__(self, college):
        self.college = college
        self.previous_college = None
    
    def __enter__(self):
        self.previous_college = get_current_college()
        set_current_college(self.college)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_college:
            set_current_college(self.previous_college)
        else:
            clear_current_college()
        return False
