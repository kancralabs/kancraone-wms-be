from django.urls import path

from .auth_views import ChangePasswordView
from .auth_views import CustomTokenRefreshView
from .auth_views import GetMeView
from .auth_views import LoginView
from .auth_views import LogoutView
from .auth_views import RegisterView
from .auth_views import ResetPasswordConfirmView
from .auth_views import ResetPasswordRequestView

app_name = "auth"

urlpatterns = [
    # Authentication
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", GetMeView.as_view(), name="me"),

    # Token Management
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),

    # Password Management
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("reset-password/", ResetPasswordRequestView.as_view(), name="reset_password_request"),  # noqa: E501
    path("reset-password/confirm/", ResetPasswordConfirmView.as_view(), name="reset_password_confirm"),  # noqa: E501
]
