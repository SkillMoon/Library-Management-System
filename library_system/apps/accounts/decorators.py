from django.core.exceptions import PermissionDenied
from functools import wraps


def role_required(*roles):
    """
    دسترسی را بر اساس نقش کاربر کنترل می‌کند.
    مثال: @role_required('admin', 'librarian')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
