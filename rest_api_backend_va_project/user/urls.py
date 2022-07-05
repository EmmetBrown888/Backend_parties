from django.urls import path

from .views import *

urlpatterns = [
    # Get all users
    path('all', UserListView.as_view()),

    # Get user for id
    path('user/<int:pk>/', UserRetrieveAPIView.as_view()),

    # Update my data
    path('update/<int:pk>/', UserUpdateData.as_view()),

    # Information about me
    path('me/', GetDataAboutMe.as_view()),

    # Auth
    # Registration
    path('auth/signup', RegisterView.as_view()),

    # Login
    path('auth/verify-code', VerifyCode.as_view(), name='verify-code'),

    # Forget password
    path('auth/forget-password', ForgetPassword.as_view(), name='forget-password'),
    path('auth/verify-forget-password', VerifyForgetPassword.as_view(), name='verify-forget-password'),
    path('auth/addPassword-forget-password', AddPasswordForgetPassword.as_view(), name='addPassword-forget-password'),

    # Change password
    path('auth/change-password', ChangePasswordView.as_view(), name='change-password'),

    # Subscription
    path('subscribers/', SubscriptionAPIView.as_view()),
    path('my_subscriber/', MySubscriber.as_view()),
]
