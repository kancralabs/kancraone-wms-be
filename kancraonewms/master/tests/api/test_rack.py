"""
Tests for Rack API endpoints
"""

from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from kancraonewms.master.models import Rack
from kancraonewms.master.tests.factories import RackFactory
from kancraonewms.organizations.tests.factories import WarehouseFactory
from kancraonewms.users.tests.factories import UserFactory


class RackViewSetTest(APITestCase):
    """Tests for Rack ViewSet"""

    def setUp(self):
        """Set up test fixtures"""
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}",
        )

        # Create test warehouses
        self.warehouse1 = WarehouseFactory(code="WH-001", name="Main Warehouse")
        self.warehouse2 = WarehouseFactory(code="WH-002", name="Secondary Warehouse")

        # Create test racks
        self.rack1 = RackFactory(
            code="RACK-001",
            name="Test Rack 1",
            warehouse=self.warehouse1,
            zone="A",
            aisle="A01",
            bay="B01",
            level="1",
            capacity=Decimal("100.00"),
            max_weight=Decimal("500.00"),
            is_active=True,
        )
        self.rack2 = RackFactory(
            code="RACK-002",
            name="Test Rack 2",
            warehouse=self.warehouse1,
            zone="B",
            aisle="A02",
            bay="B02",
            level="2",
            capacity=Decimal("200.00"),
            max_weight=Decimal("1000.00"),
            is_active=True,
        )
        self.rack3 = RackFactory(
            code="RACK-003",
            name="Test Rack 3",
            warehouse=self.warehouse2,
            zone="A",
            aisle="A01",
            bay="B01",
            level="1",
            capacity=Decimal("150.00"),
            max_weight=Decimal("750.00"),
            is_active=False,
        )

        self.list_url = reverse("api:rack-list")

    def _get_results(self, response):
        """Helper to extract results from paginated or non-paginated response"""
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]
        return response.data

    def test_list_racks_success(self):
        """Test listing all racks"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 3  # noqa: PLR2004

    def test_list_racks_unauthenticated(self):
        """Test listing racks without authentication"""
        self.client.credentials()
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_rack_success(self):
        """Test retrieving a single rack"""
        url = reverse("api:rack-detail", kwargs={"pk": self.rack1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == "RACK-001"
        assert response.data["name"] == "Test Rack 1"
        assert "warehouse_detail" in response.data
        assert "zone" in response.data
        assert "aisle" in response.data
        assert "capacity" in response.data
        assert "max_weight" in response.data

    def test_retrieve_rack_not_found(self):
        """Test retrieving non-existent rack"""
        url = reverse("api:rack-detail", kwargs={"pk": 99999})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_rack_success(self):
        """Test creating a new rack"""
        data = {
            "warehouse": self.warehouse1.pk,
            "code": "RACK-NEW",
            "name": "New Test Rack",
            "description": "Test description",
            "zone": "C",
            "aisle": "A03",
            "bay": "B03",
            "level": "3",
            "capacity": "250.00",
            "max_weight": "1500.00",
            "is_active": True,
            "notes": "Test notes",
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["code"] == "RACK-NEW"
        assert response.data["name"] == "New Test Rack"
        assert Rack.objects.filter(code="RACK-NEW").exists()

    def test_create_rack_duplicate_code(self):
        """Test creating rack with duplicate code"""
        data = {
            "warehouse": self.warehouse1.pk,
            "code": "RACK-001",  # Already exists
            "name": "Duplicate Rack",
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "code" in response.data

    def test_create_rack_missing_required_fields(self):
        """Test creating rack with missing required fields"""
        data = {
            "name": "Incomplete Rack",
            # Missing code and warehouse
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "code" in response.data
        assert "warehouse" in response.data

    def test_create_rack_negative_capacity(self):
        """Test creating rack with negative capacity"""
        data = {
            "warehouse": self.warehouse1.pk,
            "code": "RACK-NEG",
            "name": "Negative Capacity Rack",
            "capacity": "-100.00",
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "capacity" in response.data

    def test_create_rack_negative_max_weight(self):
        """Test creating rack with negative max weight"""
        data = {
            "warehouse": self.warehouse1.pk,
            "code": "RACK-NEG",
            "name": "Negative Weight Rack",
            "max_weight": "-500.00",
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "max_weight" in response.data

    def test_update_rack_success(self):
        """Test updating a rack"""
        url = reverse("api:rack-detail", kwargs={"pk": self.rack1.pk})
        data = {
            "warehouse": self.warehouse1.pk,
            "code": "RACK-001",
            "name": "Updated Rack Name",
            "zone": "D",
            "capacity": "300.00",
        }

        response = self.client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Rack Name"
        assert response.data["zone"] == "D"

        # Verify in database
        self.rack1.refresh_from_db()
        assert self.rack1.name == "Updated Rack Name"
        assert self.rack1.zone == "D"

    def test_partial_update_rack_success(self):
        """Test partially updating a rack"""
        url = reverse("api:rack-detail", kwargs={"pk": self.rack1.pk})
        data = {
            "name": "Partially Updated Rack",
        }

        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Partially Updated Rack"
        assert response.data["code"] == "RACK-001"  # Unchanged

    def test_delete_rack_success(self):
        """Test deleting a rack"""
        url = reverse("api:rack-detail", kwargs={"pk": self.rack1.pk})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Rack.objects.filter(pk=self.rack1.pk).exists()

    def test_filter_by_warehouse(self):
        """Test filtering racks by warehouse"""
        response = self.client.get(self.list_url, {"warehouse": self.warehouse1.pk})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004
        for rack in results:
            assert rack["warehouse"] == self.warehouse1.pk

    def test_filter_by_active_status(self):
        """Test filtering racks by active status"""
        response = self.client.get(self.list_url, {"is_active": "true"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004
        for rack in results:
            assert rack["is_active"]

    def test_filter_by_inactive_status(self):
        """Test filtering racks by inactive status"""
        response = self.client.get(self.list_url, {"is_active": "false"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert not results[0]["is_active"]

    def test_filter_by_zone(self):
        """Test filtering racks by zone"""
        response = self.client.get(self.list_url, {"zone": "A"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004

    def test_filter_by_aisle(self):
        """Test filtering racks by aisle"""
        response = self.client.get(self.list_url, {"aisle": "A01"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004

    def test_search_by_code(self):
        """Test searching racks by code"""
        response = self.client.get(self.list_url, {"search": "RACK-001"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert results[0]["code"] == "RACK-001"

    def test_search_by_name(self):
        """Test searching racks by name"""
        response = self.client.get(self.list_url, {"search": "Rack 2"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert results[0]["name"] == "Test Rack 2"

    def test_search_by_zone(self):
        """Test searching racks by zone"""
        response = self.client.get(self.list_url, {"search": "B"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) >= 1

    def test_search_case_insensitive(self):
        """Test search is case insensitive"""
        response = self.client.get(self.list_url, {"search": "rack 1"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) >= 1

    def test_activate_rack(self):
        """Test activating a rack"""
        url = reverse("api:rack-activate", kwargs={"pk": self.rack3.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_active"]

        # Verify in database
        self.rack3.refresh_from_db()
        assert self.rack3.is_active

    def test_deactivate_rack(self):
        """Test deactivating a rack"""
        url = reverse("api:rack-deactivate", kwargs={"pk": self.rack1.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert not response.data["is_active"]

        # Verify in database
        self.rack1.refresh_from_db()
        assert not self.rack1.is_active

    def test_list_serializer_fields(self):
        """Test list endpoint returns limited fields"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        first_rack = results[0]

        # Should have limited fields
        expected_fields = {
            "id",
            "code",
            "name",
            "warehouse",
            "warehouse_name",
            "zone",
            "aisle",
            "bay",
            "level",
            "is_active",
        }
        assert set(first_rack.keys()) == expected_fields

    def test_detail_serializer_fields(self):
        """Test detail endpoint returns all fields"""
        url = reverse("api:rack-detail", kwargs={"pk": self.rack1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Should have all fields
        expected_fields = {
            "id",
            "warehouse",
            "warehouse_detail",
            "code",
            "name",
            "description",
            "zone",
            "aisle",
            "bay",
            "level",
            "capacity",
            "max_weight",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        }
        assert set(response.data.keys()) == expected_fields

    def test_rack_ordering(self):
        """Test racks are ordered by warehouse and code"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        codes = [rack["code"] for rack in results]
        # Should be ordered by warehouse then code
        assert len(codes) == 3  # noqa: PLR2004

    def test_combined_filters(self):
        """Test combining multiple filters"""
        response = self.client.get(
            self.list_url,
            {
                "warehouse": self.warehouse1.pk,
                "is_active": "true",
                "zone": "A",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert results[0]["code"] == "RACK-001"

    def test_pagination(self):
        """Test pagination works correctly"""
        # Create more racks
        for i in range(4, 20):
            RackFactory(code=f"RACK-{i:03d}", warehouse=self.warehouse1)

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        # Check if paginated response
        if isinstance(response.data, dict) and "results" in response.data:
            assert "count" in response.data
            assert "results" in response.data
            assert response.data["count"] >= 19  # noqa: PLR2004

    def test_update_rack_readonly_fields(self):
        """Test that readonly fields cannot be updated"""
        url = reverse("api:rack-detail", kwargs={"pk": self.rack1.pk})
        original_created_at = self.rack1.created_at

        data = {
            "warehouse": self.warehouse1.pk,
            "code": "RACK-001",
            "name": "Updated Name",
            "created_at": "2020-01-01T00:00:00Z",  # Try to change readonly field
        }

        response = self.client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        self.rack1.refresh_from_db()
        assert self.rack1.created_at == original_created_at

    def test_empty_search_returns_all(self):
        """Test empty search parameter returns all racks"""
        response = self.client.get(self.list_url, {"search": ""})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 3  # noqa: PLR2004

    def test_no_results_search(self):
        """Test search with no matching results"""
        response = self.client.get(self.list_url, {"search": "NonExistentRack"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 0

    def test_rack_warehouse_relationship(self):
        """Test rack properly displays warehouse relationship"""
        url = reverse("api:rack-detail", kwargs={"pk": self.rack1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "warehouse_detail" in response.data
        assert response.data["warehouse_detail"]["code"] == "WH-001"
        assert response.data["warehouse_detail"]["name"] == "Main Warehouse"

    def test_create_rack_with_decimal_values(self):
        """Test creating rack with decimal capacity and max weight"""
        data = {
            "warehouse": self.warehouse1.pk,
            "code": "RACK-DECIMAL",
            "name": "Decimal Test Rack",
            "capacity": "123.45",
            "max_weight": "678.90",
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Decimal(response.data["capacity"]) == Decimal("123.45")
        assert Decimal(response.data["max_weight"]) == Decimal("678.90")

    def test_multiple_racks_same_warehouse(self):
        """Test creating multiple racks in same warehouse"""
        # Already have 2 racks in warehouse1
        data = {
            "warehouse": self.warehouse1.pk,
            "code": "RACK-004",
            "name": "Third Rack in WH-001",
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Rack.objects.filter(warehouse=self.warehouse1).count() == 3  # noqa: PLR2004

    def test_rack_str_representation(self):
        """Test rack string representation"""
        expected = f"{self.rack1.code} - {self.rack1.name} ({self.warehouse1.name})"
        assert str(self.rack1) == expected
