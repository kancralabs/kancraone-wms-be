"""
Tests for RoleMenuAccess API endpoints
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from kancraonewms.master.models import RoleMenuAccess
from kancraonewms.master.tests.factories import MenuFactory
from kancraonewms.master.tests.factories import RoleFactory
from kancraonewms.master.tests.factories import RoleMenuAccessFactory
from kancraonewms.users.tests.factories import UserFactory


class RoleMenuAccessViewSetTest(APITestCase):
    """Tests for RoleMenuAccess ViewSet"""

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

        # Create test menus
        self.menu1 = MenuFactory(
            code="MASTER",
            name="Master Data",
            parent=None,
            is_active=True,
        )
        self.menu2 = MenuFactory(
            code="INVENTORY",
            name="Inventory",
            parent=None,
            is_active=True,
        )
        self.menu3 = MenuFactory(
            code="MASTER_ITEM",
            name="Items",
            parent=self.menu1,
            is_active=True,
        )

        # Create test role menu accesses
        self.access1 = RoleMenuAccessFactory(
            role=self.role1,
            menu=self.menu1,
            can_access=True,
        )
        self.access2 = RoleMenuAccessFactory(
            role=self.role1,
            menu=self.menu2,
            can_access=True,
        )
        self.access3 = RoleMenuAccessFactory(
            role=self.role2,
            menu=self.menu1,
            can_access=False,
        )

        self.list_url = reverse("api:rolemenuaccess-list")

    def _get_results(self, response):
        """Helper to extract results from paginated or non-paginated response"""
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]
        return response.data

    def test_list_role_menu_accesses_success(self):
        """Test listing all role menu accesses"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 3  # noqa: PLR2004

    def test_list_role_menu_accesses_unauthenticated(self):
        """Test listing role menu accesses without authentication"""
        self.client.credentials()
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_role_menu_access_success(self):
        """Test retrieving a single role menu access"""
        url = reverse("api:rolemenuaccess-detail", kwargs={"pk": self.access1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["role"] == self.role1.pk
        assert response.data["menu"] == self.menu1.pk
        assert response.data["can_access"] is True

    def test_create_role_menu_access_success(self):
        """Test creating a new role menu access"""
        data = {
            "role": self.role2.pk,
            "menu": self.menu2.pk,
            "can_access": True,
        }
        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert RoleMenuAccess.objects.filter(
            role=self.role2,
            menu=self.menu2,
        ).exists()

    def test_update_role_menu_access_success(self):
        """Test updating a role menu access"""
        url = reverse("api:rolemenuaccess-detail", kwargs={"pk": self.access1.pk})
        data = {
            "role": self.role1.pk,
            "menu": self.menu1.pk,
            "can_access": False,
        }
        response = self.client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        self.access1.refresh_from_db()
        assert self.access1.can_access is False

    def test_delete_role_menu_access_success(self):
        """Test deleting a role menu access"""
        url = reverse("api:rolemenuaccess-detail", kwargs={"pk": self.access3.pk})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not RoleMenuAccess.objects.filter(pk=self.access3.pk).exists()

    def test_filter_by_role(self):
        """Test filtering role menu accesses by role"""
        response = self.client.get(self.list_url, {"role": self.role1.pk})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004

    def test_filter_by_menu(self):
        """Test filtering role menu accesses by menu"""
        response = self.client.get(self.list_url, {"menu": self.menu1.pk})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004

    def test_filter_by_can_access(self):
        """Test filtering role menu accesses by can_access"""
        response = self.client.get(self.list_url, {"can_access": "true"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004

    def test_get_by_role_action(self):
        """Test getting role menu accesses by role via action"""
        url = reverse("api:rolemenuaccess-by-role")
        response = self.client.get(url, {"role_id": self.role1.pk})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # noqa: PLR2004

    def test_get_accessible_menus(self):
        """Test getting accessible menus for a role"""
        url = reverse("api:rolemenuaccess-accessible-menus")
        response = self.client.get(url, {"role_id": self.role1.pk})

        assert response.status_code == status.HTTP_200_OK
        # Should return menu tree structure with only accessible menus
        assert len(response.data) == 2  # noqa: PLR2004

    def test_grant_access(self):
        """Test granting access to menu"""
        url = reverse("api:rolemenuaccess-grant", kwargs={"pk": self.access3.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        self.access3.refresh_from_db()
        assert self.access3.can_access is True

    def test_revoke_access(self):
        """Test revoking access to menu"""
        url = reverse("api:rolemenuaccess-revoke", kwargs={"pk": self.access1.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        self.access1.refresh_from_db()
        assert self.access1.can_access is False
