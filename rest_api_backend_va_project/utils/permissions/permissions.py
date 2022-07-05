from rest_framework.permissions import BasePermission


class AccountIsVerified(BasePermission):
    """Check user confirm email and account"""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.confirm_email and
            request.user.confirm_account
        )


class EmailIsVerified(BasePermission):
    """Check user only confirm email"""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.confirm_email)
