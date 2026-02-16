from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from .auth_serializers import ChangePasswordSerializer
from .auth_serializers import LoginSerializer
from .auth_serializers import RegisterSerializer
from .auth_serializers import ResetPasswordConfirmSerializer
from .auth_serializers import ResetPasswordRequestSerializer
from .auth_serializers import UserProfileSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API endpoint untuk registrasi user baru
    """

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens untuk user baru
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": user.name,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """
    API endpoint untuk login dengan username/password
    Returns: access token, refresh token, dan user info
    """

    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer


class LogoutView(APIView):
    """
    API endpoint untuk logout (blacklist refresh token)
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:  # noqa: BLE001
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GetMeView(APIView):
    """
    API endpoint untuk mendapatkan info user yang sedang login (by token)
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    API endpoint untuk ubah password user yang sedang login
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordRequestView(APIView):
    """
    API endpoint untuk request reset password
    Mengirim email dengan token reset password
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)

            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Kirim email (customize sesuai kebutuhan)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

            try:
                send_mail(
                    subject="Reset Password Request",
                    message=f"Click this link to reset your password: {reset_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                return Response(
                    {
                        "message": "Password reset email has been sent",
                        "token": token,
                        "uid": uid,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception:  # noqa: BLE001
                return Response(
                    {"error": "Failed to send email. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirmView(APIView):
    """
    API endpoint untuk konfirmasi reset password dengan token
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data["token"]
            uid = request.data.get("uid")
            new_password = serializer.validated_data["new_password"]

            try:
                # Decode uid
                user_id = urlsafe_base64_decode(uid).decode()
                user = User.objects.get(pk=user_id)

                # Verify token
                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()

                    return Response(
                        {"message": "Password has been reset successfully"},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"error": "Invalid or expired token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response(
                    {"error": "Invalid token or user ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Custom Refresh Token View (optional, bisa pakai bawaan)
class CustomTokenRefreshView(TokenRefreshView):
    """
    API endpoint untuk refresh access token
    """

    permission_classes = (AllowAny,)
