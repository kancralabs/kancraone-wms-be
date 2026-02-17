"""
Tests for Menu API endpoints
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from kancraonewms.master.models import Menu
from kancraonewms.master.tests.factories import MenuFactory
from kancraonewms.users.tests.factories import UserFactory


class MenuViewSetTest(APITestCase):
    """Tests for Menu ViewSet"""

    def setUp(self):
        """Set up test fixtures"""
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}",
        )

        # Create parent menus
        self.menu1 = MenuFactory(
            code="MASTER",
            name="Master Data",
            icon="database",
            url="/master",
            parent=None,
            order=1,
            is_active=True,
            module="master",
        )
        self.menu2 = MenuFactory(
            code="INVENTORY",
            name="Inventory",
            icon="warehouse",
            url="/inventory",
            parent=None,
            order=2,
            is_active=True,
            module="inventory",
        )

        # Create child menus
        self.menu3 = MenuFactory(
            code="MASTER_ITEM",
            name="Items",
            icon="box",
            url="/master/items",
            parent=self.menu1,
            order=1,
            is_active=True,
            module="master",
        )
        self.menu4 = MenuFactory(
            code="MASTER_UOM",
            name="UOM",
            icon="ruler",
            url="/master/uom",
            parent=self.menu1,
            order=2,
            is_active=False,
            module="master",
        )

        self.list_url = reverse("api:menu-list")

    def _get_results(self, response):
        """Helper to extract results from paginated or non-paginated response"""
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]
        return response.data

    def test_list_menus_success(self):
        """Test listing all menus"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 4  # noqa: PLR2004

    def test_list_menus_unauthenticated(self):
        """Test listing menus without authentication"""
        self.client.credentials()
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_menu_success(self):
        """Test retrieving a single menu"""
        url = reverse("api:menu-detail", kwargs={"pk": self.menu1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == "MASTER"
        assert response.data["name"] == "Master Data"

    def test_create_menu_success(self):
        """Test creating a new menu"""
        data = {
            "code": "REPORTS",
            "name": "Reports",
            "icon": "chart",
            "url": "/reports",
            "order": 3,
            "is_active": True,
            "module": "report",
        }
        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Menu.objects.filter(code="REPORTS").exists()

    def test_update_menu_success(self):
        """Test updating a menu"""
        url = reverse("api:menu-detail", kwargs={"pk": self.menu1.pk})
        data = {
            "code": "MASTER",
            "name": "Master Data Management",
            "icon": "database",
            "url": "/master",
            "order": 1,
            "is_active": True,
            "module": "master",
        }
        response = self.client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        self.menu1.refresh_from_db()
        assert self.menu1.name == "Master Data Management"

    def test_delete_menu_success(self):
        """Test deleting a menu"""
        url = reverse("api:menu-detail", kwargs={"pk": self.menu4.pk})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Menu.objects.filter(pk=self.menu4.pk).exists()

    def test_search_menus(self):
        """Test searching menus"""
        response = self.client.get(self.list_url, {"search": "Items"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert results[0]["code"] == "MASTER_ITEM"

    def test_filter_active_menus(self):
        """Test filtering active menus"""
        response = self.client.get(self.list_url, {"is_active": "true"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 3  # noqa: PLR2004

    def test_filter_by_module(self):
        """Test filtering menus by module"""
        response = self.client.get(self.list_url, {"module": "master"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 3  # noqa: PLR2004

    def test_get_active_menus(self):
        """Test getting only active menus via action"""
        url = reverse("api:menu-active")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3  # noqa: PLR2004

    def test_get_menu_tree(self):
        """Test getting menu tree structure"""
        url = reverse("api:menu-tree")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # Only parent menus  # noqa: PLR2004
        # Check if children are included
        master_menu = next(m for m in response.data if m["code"] == "MASTER")
        assert "children" in master_menu
        assert len(master_menu["children"]) == 1  # Only active child

    def test_get_root_menus(self):
        """Test getting root menus (without parent)"""
        url = reverse("api:menu-roots")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004

    def test_get_menu_children(self):
        """Test getting children of a menu"""
        url = reverse("api:menu-children", kwargs={"pk": self.menu1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004

    def test_activate_menu(self):
        """Test activating a menu"""
        url = reverse("api:menu-activate", kwargs={"pk": self.menu4.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        self.menu4.refresh_from_db()
        assert self.menu4.is_active is True

    def test_deactivate_menu(self):
        """Test deactivating a menu"""
        url = reverse("api:menu-deactivate", kwargs={"pk": self.menu1.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        self.menu1.refresh_from_db()
        assert self.menu1.is_active is False
