"""
Tests for Company API endpoints
"""

from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from kancraonewms.organizations.models import Company
from kancraonewms.organizations.tests.factories import CompanyFactory
from kancraonewms.users.tests.factories import UserFactory


class CompanyViewSetTest(APITestCase):
    """Tests for Company ViewSet"""

    def setUp(self):
        """Set up test fixtures"""
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}",
        )

        # Create test companies
        self.company1 = CompanyFactory(
            code="COMP-001",
            name="Test Company 1",
            company_type="customer",
            city="Jakarta",
            country="Indonesia",
            is_active=True,
        )
        self.company2 = CompanyFactory(
            code="COMP-002",
            name="Test Company 2",
            company_type="vendor",
            city="Bandung",
            country="Indonesia",
            is_active=True,
        )
        self.company3 = CompanyFactory(
            code="COMP-003",
            name="Test Company 3",
            company_type="both",
            city="Surabaya",
            country="Indonesia",
            is_active=False,
        )

        self.list_url = reverse("api:company-list")

    def _get_results(self, response):
        """Helper to extract results from paginated or non-paginated response"""
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]
        return response.data

    def test_list_companies_success(self):
        """Test listing all companies"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 3  # noqa: PLR2004

    def test_list_companies_unauthenticated(self):
        """Test listing companies without authentication"""
        self.client.credentials()
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_company_success(self):
        """Test retrieving a single company"""
        url = reverse("api:company-detail", kwargs={"pk": self.company1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == "COMP-001"
        assert response.data["name"] == "Test Company 1"
        assert "tax_id" in response.data
        assert "phone" in response.data
        assert "email" in response.data

    def test_retrieve_company_not_found(self):
        """Test retrieving non-existent company"""
        url = reverse("api:company-detail", kwargs={"pk": 99999})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_company_success(self):
        """Test creating a new company"""
        data = {
            "code": "COMP-NEW",
            "name": "New Test Company",
            "legal_name": "New Test Company Ltd",
            "company_type": "customer",
            "tax_id": "12.345.678.9-012.345",
            "phone": "+62-21-12345678",
            "email": "contact@newcompany.com",
            "website": "https://newcompany.com",
            "address": "Jl. Test No. 123",
            "city": "Jakarta",
            "state": "DKI Jakarta",
            "postal_code": "12345",
            "country": "Indonesia",
            "currency": "IDR",
            "payment_terms": 30,
            "credit_limit": "1000000.00",
            "notes": "Test notes",
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["code"] == "COMP-NEW"
        assert response.data["name"] == "New Test Company"
        assert Company.objects.filter(code="COMP-NEW").exists()

    def test_create_company_duplicate_code(self):
        """Test creating company with duplicate code"""
        data = {
            "code": "COMP-001",  # Already exists
            "name": "Duplicate Company",
            "company_type": "customer",
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "code" in response.data

    def test_create_company_missing_required_fields(self):
        """Test creating company with missing required fields"""
        data = {
            "name": "Incomplete Company",
            # Missing code
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "code" in response.data

    def test_update_company_success(self):
        """Test updating a company"""
        url = reverse("api:company-detail", kwargs={"pk": self.company1.pk})
        data = {
            "code": "COMP-001",
            "name": "Updated Company Name",
            "company_type": "vendor",
            "city": "Medan",
        }

        response = self.client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Company Name"
        assert response.data["company_type"] == "vendor"

        # Verify in database
        self.company1.refresh_from_db()
        assert self.company1.name == "Updated Company Name"
        assert self.company1.company_type == "vendor"

    def test_partial_update_company_success(self):
        """Test partially updating a company"""
        url = reverse("api:company-detail", kwargs={"pk": self.company1.pk})
        data = {
            "name": "Partially Updated Company",
        }

        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Partially Updated Company"
        assert response.data["code"] == "COMP-001"  # Unchanged

    def test_delete_company_success(self):
        """Test deleting a company"""
        url = reverse("api:company-detail", kwargs={"pk": self.company1.pk})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Company.objects.filter(pk=self.company1.pk).exists()

    def test_filter_by_active_status(self):
        """Test filtering companies by active status"""
        response = self.client.get(self.list_url, {"is_active": "true"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 2  # noqa: PLR2004
        for company in results:
            assert company["is_active"]

    def test_filter_by_inactive_status(self):
        """Test filtering companies by inactive status"""
        response = self.client.get(self.list_url, {"is_active": "false"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert not results[0]["is_active"]

    def test_filter_by_company_type(self):
        """Test filtering companies by type"""
        response = self.client.get(self.list_url, {"company_type": "customer"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert results[0]["code"] == "COMP-001"

    def test_filter_by_country(self):
        """Test filtering companies by country"""
        # Create company with different country
        CompanyFactory(code="COMP-US", country="USA")

        response = self.client.get(self.list_url, {"country": "USA"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert results[0]["code"] == "COMP-US"

    def test_search_by_code(self):
        """Test searching companies by code"""
        response = self.client.get(self.list_url, {"search": "COMP-001"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert results[0]["code"] == "COMP-001"

    def test_search_by_name(self):
        """Test searching companies by name"""
        response = self.client.get(self.list_url, {"search": "Company 2"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert results[0]["name"] == "Test Company 2"

    def test_search_by_city(self):
        """Test searching companies by city"""
        response = self.client.get(self.list_url, {"search": "Bandung"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert results[0]["city"] == "Bandung"

    def test_search_case_insensitive(self):
        """Test search is case insensitive"""
        response = self.client.get(self.list_url, {"search": "company 1"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) >= 1

    def test_activate_company(self):
        """Test activating a company"""
        url = reverse("api:company-activate", kwargs={"pk": self.company3.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_active"]

        # Verify in database
        self.company3.refresh_from_db()
        assert self.company3.is_active

    def test_deactivate_company(self):
        """Test deactivating a company"""
        url = reverse("api:company-deactivate", kwargs={"pk": self.company1.pk})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert not response.data["is_active"]

        # Verify in database
        self.company1.refresh_from_db()
        assert not self.company1.is_active

    def test_list_serializer_fields(self):
        """Test list endpoint returns limited fields"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        first_company = results[0]

        # Should have limited fields
        expected_fields = {
            "id",
            "code",
            "name",
            "company_type",
            "city",
            "country",
            "is_active",
        }
        assert set(first_company.keys()) == expected_fields

    def test_detail_serializer_fields(self):
        """Test detail endpoint returns all fields"""
        url = reverse("api:company-detail", kwargs={"pk": self.company1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Should have all fields
        expected_fields = {
            "id",
            "code",
            "name",
            "legal_name",
            "company_type",
            "tax_id",
            "phone",
            "email",
            "website",
            "address",
            "city",
            "state",
            "postal_code",
            "country",
            "currency",
            "payment_terms",
            "credit_limit",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        }
        assert set(response.data.keys()) == expected_fields

    def test_company_ordering(self):
        """Test companies are ordered by code"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        codes = [company["code"] for company in results]
        assert codes == sorted(codes)

    def test_create_company_with_decimal_credit_limit(self):
        """Test creating company with decimal credit limit"""
        data = {
            "code": "COMP-DECIMAL",
            "name": "Decimal Test Company",
            "company_type": "customer",
            "credit_limit": "12345.67",
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Decimal(response.data["credit_limit"]) == Decimal("12345.67")

    def test_create_company_default_values(self):
        """Test company is created with correct default values"""
        data = {
            "code": "COMP-DEFAULT",
            "name": "Default Values Company",
            "company_type": "customer",
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["currency"] == "IDR"
        assert response.data["payment_terms"] == 30  # noqa: PLR2004
        assert response.data["country"] == "Indonesia"
        assert Decimal(response.data["credit_limit"]) == Decimal("0")

    def test_combined_filters(self):
        """Test combining multiple filters"""
        response = self.client.get(
            self.list_url,
            {
                "is_active": "true",
                "company_type": "customer",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 1
        assert results[0]["code"] == "COMP-001"

    def test_pagination(self):
        """Test pagination works correctly"""
        # Create more companies with unique codes
        for i in range(4, 20):  # Start from 4 to avoid conflicts
            CompanyFactory(code=f"COMP-{i:03d}")

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        # Check if paginated response
        if isinstance(response.data, dict) and "results" in response.data:
            assert "count" in response.data
            assert "results" in response.data
            assert response.data["count"] >= 19  # noqa: PLR2004

    def test_update_company_readonly_fields(self):
        """Test that readonly fields cannot be updated"""
        url = reverse("api:company-detail", kwargs={"pk": self.company1.pk})
        original_created_at = self.company1.created_at

        data = {
            "code": "COMP-001",
            "name": "Updated Name",
            "created_at": "2020-01-01T00:00:00Z",  # Try to change readonly field
        }

        response = self.client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        self.company1.refresh_from_db()
        assert self.company1.created_at == original_created_at

    def test_invalid_company_type(self):
        """Test creating company with invalid company type"""
        data = {
            "code": "COMP-INVALID",
            "name": "Invalid Type Company",
            "company_type": "invalid_type",
        }

        response = self.client.post(self.list_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "company_type" in response.data

    def test_empty_search_returns_all(self):
        """Test empty search parameter returns all companies"""
        response = self.client.get(self.list_url, {"search": ""})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 3  # noqa: PLR2004

    def test_no_results_search(self):
        """Test search with no matching results"""
        response = self.client.get(self.list_url, {"search": "NonExistentCompany"})

        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) == 0
