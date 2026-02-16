"""
Tests for authentication API endpoints
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from kancraonewms.users.tests.factories import UserFactory

User = get_user_model()


class RegisterViewTest(APITestCase):
    """Tests for user registration endpoint"""

    def setUp(self):
        self.url = reverse("auth:register")
        self.valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!@#",
            "password2": "TestPass123!@#",
            "name": "Test User",
        }

    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertIn("user", response.data)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["username"], "testuser")
        self.assertEqual(response.data["user"]["email"], "test@example.com")

        # Verify user is created in database
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_password_mismatch(self):
        """Test registration fails when passwords don't match"""
        data = self.valid_data.copy()
        data["password2"] = "DifferentPassword123!"

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_weak_password(self):
        """Test registration fails with weak password"""
        data = self.valid_data.copy()
        data["password"] = "123"
        data["password2"] = "123"

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        """Test registration fails with duplicate username"""
        UserFactory(username="testuser")

        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_duplicate_email(self):
        """Test registration fails with duplicate email"""
        UserFactory(email="test@example.com")

        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_missing_required_fields(self):
        """Test registration fails with missing required fields"""
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)


class LoginViewTest(APITestCase):
    """Tests for login endpoint"""

    def setUp(self):
        self.url = reverse("auth:login")
        self.password = "TestPass123!@#"
        self.user = UserFactory(username="testuser")
        self.user.set_password(self.password)
        self.user.save()

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(self.url, {
            "username": "testuser",
            "password": self.password,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "testuser")

    def test_login_invalid_password(self):
        """Test login fails with invalid password"""
        response = self.client.post(self.url, {
            "username": "testuser",
            "password": "WrongPassword123!",
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test login fails with nonexistent user"""
        response = self.client.post(self.url, {
            "username": "nonexistent",
            "password": self.password,
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_credentials(self):
        """Test login fails with missing credentials"""
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutViewTest(APITestCase):
    """Tests for logout endpoint"""

    def setUp(self):
        self.url = reverse("auth:logout")
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}")

    def test_logout_success(self):
        """Test successful logout"""
        response = self.client.post(self.url, {
            "refresh": str(self.refresh),
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_logout_without_refresh_token(self):
        """Test logout fails without refresh token"""
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_logout_invalid_refresh_token(self):
        """Test logout fails with invalid refresh token"""
        response = self.client.post(self.url, {
            "refresh": "invalid_token",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_logout_unauthenticated(self):
        """Test logout requires authentication"""
        self.client.credentials()
        response = self.client.post(self.url, {
            "refresh": str(self.refresh),
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetMeViewTest(APITestCase):
    """Tests for get me (profile) endpoint"""

    def setUp(self):
        self.url = reverse("auth:me")
        self.user = UserFactory(
            username="testuser",
            email="test@example.com",
            name="Test User",
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}")

    def test_get_me_success(self):
        """Test successful retrieval of current user profile"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["name"], "Test User")
        self.assertIn("id", response.data)
        self.assertIn("date_joined", response.data)
        self.assertIn("is_active", response.data)

    def test_get_me_unauthenticated(self):
        """Test get me fails without authentication"""
        self.client.credentials()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordViewTest(APITestCase):
    """Tests for change password endpoint"""

    def setUp(self):
        self.url = reverse("auth:change-password")
        self.old_password = "OldPass123!@#"
        self.user = UserFactory()
        self.user.set_password(self.old_password)
        self.user.save()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}")

    def test_change_password_success(self):
        """Test successful password change"""
        response = self.client.post(self.url, {
            "old_password": self.old_password,
            "new_password": "NewPass123!@#",
            "new_password2": "NewPass123!@#",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        # Verify password is changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass123!@#"))

    def test_change_password_wrong_old_password(self):
        """Test password change fails with wrong old password"""
        response = self.client.post(self.url, {
            "old_password": "WrongPassword123!",
            "new_password": "NewPass123!@#",
            "new_password2": "NewPass123!@#",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)

    def test_change_password_mismatch(self):
        """Test password change fails when new passwords don't match"""
        response = self.client.post(self.url, {
            "old_password": self.old_password,
            "new_password": "NewPass123!@#",
            "new_password2": "DifferentPass123!",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_change_password_weak_password(self):
        """Test password change fails with weak password"""
        response = self.client.post(self.url, {
            "old_password": self.old_password,
            "new_password": "123",
            "new_password2": "123",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        """Test password change requires authentication"""
        self.client.credentials()
        response = self.client.post(self.url, {
            "old_password": self.old_password,
            "new_password": "NewPass123!@#",
            "new_password2": "NewPass123!@#",
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="test@example.com",
    FRONTEND_URL="http://localhost:3000",
)
class ResetPasswordRequestViewTest(APITestCase):
    """Tests for password reset request endpoint"""

    def setUp(self):
        self.url = reverse("auth:reset-password-request")
        self.user = UserFactory(email="test@example.com")

    def test_reset_password_request_success(self):
        """Test successful password reset request"""
        response = self.client.post(self.url, {
            "email": "test@example.com",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("token", response.data)
        self.assertIn("uid", response.data)

    def test_reset_password_request_nonexistent_email(self):
        """Test password reset request fails with nonexistent email"""
        response = self.client.post(self.url, {
            "email": "nonexistent@example.com",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_reset_password_request_invalid_email(self):
        """Test password reset request fails with invalid email"""
        response = self.client.post(self.url, {
            "email": "invalid-email",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("kancraonewms.users.api.auth_views.send_mail")
    def test_reset_password_request_email_failure(self, mock_send_mail):
        """Test password reset request handles email failure"""
        mock_send_mail.side_effect = Exception("Email service error")

        response = self.client.post(self.url, {
            "email": "test@example.com",
        })

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)


class ResetPasswordConfirmViewTest(APITestCase):
    """Tests for password reset confirmation endpoint"""

    def setUp(self):
        self.url = reverse("auth:reset-password-confirm")
        self.user = UserFactory()
        self.token = default_token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))

    def test_reset_password_confirm_success(self):
        """Test successful password reset"""
        response = self.client.post(self.url, {
            "uid": self.uid,
            "token": self.token,
            "new_password": "NewPassword123!@#",
            "new_password2": "NewPassword123!@#",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        # Verify password is changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123!@#"))

    def test_reset_password_confirm_invalid_token(self):
        """Test password reset fails with invalid token"""
        response = self.client.post(self.url, {
            "uid": self.uid,
            "token": "invalid-token",
            "new_password": "NewPassword123!@#",
            "new_password2": "NewPassword123!@#",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_reset_password_confirm_invalid_uid(self):
        """Test password reset fails with invalid uid"""
        response = self.client.post(self.url, {
            "uid": "invalid-uid",
            "token": self.token,
            "new_password": "NewPassword123!@#",
            "new_password2": "NewPassword123!@#",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_reset_password_confirm_password_mismatch(self):
        """Test password reset fails when passwords don't match"""
        response = self.client.post(self.url, {
            "uid": self.uid,
            "token": self.token,
            "new_password": "NewPassword123!@#",
            "new_password2": "DifferentPassword123!",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_reset_password_confirm_weak_password(self):
        """Test password reset fails with weak password"""
        response = self.client.post(self.url, {
            "uid": self.uid,
            "token": self.token,
            "new_password": "123",
            "new_password2": "123",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshViewTest(APITestCase):
    """Tests for token refresh endpoint"""

    def setUp(self):
        self.url = reverse("auth:token-refresh")
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)

    def test_token_refresh_success(self):
        """Test successful token refresh"""
        response = self.client.post(self.url, {
            "refresh": str(self.refresh),
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_invalid_token(self):
        """Test token refresh fails with invalid token"""
        response = self.client.post(self.url, {
            "refresh": "invalid_token",
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_missing_token(self):
        """Test token refresh fails without token"""
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
