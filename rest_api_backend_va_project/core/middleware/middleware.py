from django.utils import timezone

from user.models import User


class UpdateLastActivityMiddleware:
    """Update field last activity"""

    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.id) \
                .update(last_activity=timezone.now())
        response = self._get_response(request)
        return response
