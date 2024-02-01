from django.shortcuts import render,redirect
from functools import wraps
def admin_only(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            # User is authenticated and is an admin
            return view_func(request, *args, **kwargs)
        else:
            # User is not an admin; redirect to a login page or a forbidden page
            return redirect('/')  # Replace 'login' with your login URL or a forbidden page URL
    return _wrapped_view