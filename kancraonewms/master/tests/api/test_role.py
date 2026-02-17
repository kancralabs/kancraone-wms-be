"""
Tests for Role API endpoints
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from kancraonewms.master.models import Role
from kancraonewms.master.tests.factories import RoleFactory
from kancraonewms.users.tests.factories import UserFactory


class RoleViewSetTest(APITestCase):
    """Tests for Role ViewSet"""

    def setUp(self):
        """Set up test fixtures"""
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}",
        )

        # Create test roles
        self.role1 = RoleFactory(
            code="ADMIN",
            name="Administrator",
            description="System administrator role",
            is_active=True,
        )
        self.role2 = RoleFactory(
            code="MANAGER",
            name="Manager",
            description="Warehouse manager role",
            is_active=True,
        )
        self.role3 = RoleFactory(
            code="OPERATOR",
            name="Operator",
            description="Warehouse operator role",
            is_active=False,
        )

        self.list_url = reverse("api:role-list")

    def _get_results(self, response):
        """Helper to extract results from paginated or non-paginated response"""
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]
        return response.data

    def test_list_roles_success(self):
        """Test listing all roles"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 3  # noqa: PLR2004

    def test_list_roles_unauthenticated(self):
        """Test listing roles without authentication"""
        self.client.credentials()
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_role_success(self):
        """Test retrieving a single role"""
        url = reverse("api:role-detail", kwargs={"pk": self.role1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == "ADMIN"
        assert response.data["name"] == "Administrator"

    def test_create_role_success(self):
        """Test creating a new role"""
        data = {
            "code": "SUPERVISOR",
            "name": "Supervisor",
            "description": "Warehouse supervisor role",
            "is_active": True,
        }
        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Role.objects.filter(code="SUPERVISOR").exists()

    def test_update_role_success(self):
        """Test updating a role"""
        url = reverse("api:role-detail", kwargs={"pk": self.role1.pk})
        data = {
            "code": "ADMIN",
            "name": "System Administrator",
            "description": "Updated description",
            "is_active": True,
        }
        response = self.client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        self.role1.refresh_from_db()
        assert self.role1.name == "System Administrator"

    def test_delete_role_success(self):
        """Test deleting a role"""
        url = reverse("api:role-detail", kwargs={"pk": self.role3.pk})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Role.objects.filter(pk=self.role3.pk).exists()

    def test_search_roles(self):
        """Test searching roles"""
        response = self.client.get(self.list_url, {"search": "Manager"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert results[0]["code"] == "MANAGER"

    def test_filter_active_roles(self):
        """Test filtering active roles"""
        response = self.client.get(self.list_url, {"is_active": "true"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004

    def test_get_active_roles(self):
        """Test getting only active roles via action"""
        url = reverse("api:role-active")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # noqa: PLR2004

    def test_activate_role(self):
        """Test activating a role"""
        url = reverse("api:role-activate", kwargs={"pk": self.role3.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        self.role3.refresh_from_db()
        assert self.role3.is_active is True

    def test_deactivate_role(self):
        """Test deactivating a role"""
        url = reverse("api:role-deactivate", kwargs={"pk": self.role1.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        self.role1.refresh_from_db()
        assert self.role1.is_active is False
