"""
Tests for Accessibility API endpoints
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from kancraonewms.master.models import Accessibility
from kancraonewms.master.tests.factories import AccessibilityFactory
from kancraonewms.master.tests.factories import RoleFactory
from kancraonewms.users.tests.factories import UserFactory


class AccessibilityViewSetTest(APITestCase):
    """Tests for Accessibility ViewSet"""

    def setUp(self):
        """Set up test fixtures"""
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}",
        )

        # Create test roles
        self.role1 = RoleFactory(code="ADMIN", name="Administrator")
        self.role2 = RoleFactory(code="MANAGER", name="Manager")

        # Create test accessibilities
        self.access1 = AccessibilityFactory(
            role=self.role1,
            module="master",
            feature="item",
            permission="create",
            is_granted=True,
        )
        self.access2 = AccessibilityFactory(
            role=self.role1,
            module="master",
            feature="item",
            permission="read",
            is_granted=True,
        )
        self.access3 = AccessibilityFactory(
            role=self.role2,
            module="inventory",
            feature="stock",
            permission="read",
            is_granted=False,
        )

        self.list_url = reverse("api:accessibility-list")

    def _get_results(self, response):
        """Helper to extract results from paginated or non-paginated response"""
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]
        return response.data

    def test_list_accessibilities_success(self):
        """Test listing all accessibilities"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 3  # noqa: PLR2004

    def test_list_accessibilities_unauthenticated(self):
        """Test listing accessibilities without authentication"""
        self.client.credentials()
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_accessibility_success(self):
        """Test retrieving a single accessibility"""
        url = reverse("api:accessibility-detail", kwargs={"pk": self.access1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["module"] == "master"
        assert response.data["feature"] == "item"
        assert response.data["permission"] == "create"

    def test_create_accessibility_success(self):
        """Test creating a new accessibility"""
        data = {
            "role": self.role1.pk,
            "module": "master",
            "feature": "uom",
            "permission": "update",
            "is_granted": True,
        }
        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Accessibility.objects.filter(
            role=self.role1,
            module="master",
            feature="uom",
            permission="update",
        ).exists()

    def test_update_accessibility_success(self):
        """Test updating an accessibility"""
        url = reverse("api:accessibility-detail", kwargs={"pk": self.access1.pk})
        data = {
            "role": self.role1.pk,
            "module": "master",
            "feature": "item",
            "permission": "create",
            "is_granted": False,
        }
        response = self.client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        self.access1.refresh_from_db()
        assert self.access1.is_granted is False

    def test_delete_accessibility_success(self):
        """Test deleting an accessibility"""
        url = reverse("api:accessibility-detail", kwargs={"pk": self.access3.pk})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Accessibility.objects.filter(pk=self.access3.pk).exists()

    def test_filter_by_role(self):
        """Test filtering accessibilities by role"""
        response = self.client.get(self.list_url, {"role": self.role1.pk})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004

    def test_filter_by_module(self):
        """Test filtering accessibilities by module"""
        response = self.client.get(self.list_url, {"module": "master"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004

    def test_filter_by_permission(self):
        """Test filtering accessibilities by permission"""
        response = self.client.get(self.list_url, {"permission": "read"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004

    def test_get_by_role_action(self):
        """Test getting accessibilities by role via action"""
        url = reverse("api:accessibility-by-role")
        response = self.client.get(url, {"role_id": self.role1.pk})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # noqa: PLR2004

    def test_grant_permission(self):
        """Test granting permission"""
        url = reverse("api:accessibility-grant", kwargs={"pk": self.access3.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        self.access3.refresh_from_db()
        assert self.access3.is_granted is True

    def test_revoke_permission(self):
        """Test revoking permission"""
        url = reverse("api:accessibility-revoke", kwargs={"pk": self.access1.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        self.access1.refresh_from_db()
        assert self.access1.is_granted is False
