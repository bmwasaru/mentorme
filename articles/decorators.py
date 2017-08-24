from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin

from authentication.models import Profile


class UserIsMentorMixin(AccessMixin):
    """Verify that the current user is a mentor"""
    def dispatch(self, request, *args, **kwargs):
        user = Profile.objects.get(user=request.user)
        if user.role != 'mentor':
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)



def user_is_mentor(function):
    def wrap(request):
        user = Profile.objects.get(user=request.user)
        if user.role == 'mentor':
            return function(request)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
