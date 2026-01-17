from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def role_required(required_role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if not hasattr(request.user, 'profile'):
                return HttpResponseForbidden("Profile not found")

            if request.user.profile.role != required_role:
                return HttpResponseForbidden("Access Denied - Insufficient Permissions")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
