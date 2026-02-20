from django.urls import path
from .views import RegisterAPIView, LoginAPIView, ResetPasswordAPIView, UserDetailAPIView, UserListAPIView, UserUpdateAPIView, VerifyOTPAPIView,RequestOTPAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),

    path('users/', UserListAPIView.as_view()),
    path('users/<int:user_id>/', UserDetailAPIView.as_view()),
    path('users/update/<int:user_id>/', UserUpdateAPIView.as_view()),
    path('password-reset/request-otp/', RequestOTPAPIView.as_view()),
    path('password-reset/verify-otp/', VerifyOTPAPIView.as_view()),
    path('password-reset/confirm/', ResetPasswordAPIView.as_view()),
]
