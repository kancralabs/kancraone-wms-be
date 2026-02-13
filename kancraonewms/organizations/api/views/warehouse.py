from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from kancraonewms.organizations.api.serializers import WarehouseCreateUpdateSerializer
from kancraonewms.organizations.api.serializers import WarehouseListSerializer
from kancraonewms.organizations.api.serializers import WarehouseSerializer
from kancraonewms.organizations.models import Warehouse


class WarehouseViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet untuk Warehouse model"""

    queryset = Warehouse.objects.select_related("company").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return WarehouseListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return WarehouseCreateUpdateSerializer
        return WarehouseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by company
        company_id = self.request.query_params.get("company")
        if company_id:
            queryset = queryset.filter(company_id=company_id)

        # Filter by active status
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # Filter by default status
        is_default = self.request.query_params.get("is_default")
        if is_default is not None:
            queryset = queryset.filter(is_default=is_default.lower() == "true")

        # Filter by country
        country = self.request.query_params.get("country")
        if country:
            queryset = queryset.filter(country__iexact=country)

        # Filter by city
        city = self.request.query_params.get("city")
        if city:
            queryset = queryset.filter(city__iexact=city)

        # Search by code, name, company name, or city
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(company__name__icontains=search)
                | Q(city__icontains=search),
            )

        return queryset

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a warehouse"""
        warehouse = self.get_object()
        warehouse.is_active = True
        warehouse.save()
        serializer = self.get_serializer(warehouse)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a warehouse"""
        warehouse = self.get_object()
        warehouse.is_active = False
        warehouse.save()
        serializer = self.get_serializer(warehouse)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def set_as_default(self, request, pk=None):
        """Set this warehouse as the default for its company"""
        warehouse = self.get_object()
        warehouse.is_default = True
        warehouse.save()
        serializer = self.get_serializer(warehouse)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_company(self, request):
        """Get warehouses grouped by company"""
        company_id = request.query_params.get("company_id")
        if not company_id:
            return Response({"error": "company_id parameter is required"}, status=400)

        warehouses = self.get_queryset().filter(company_id=company_id)
        serializer = self.get_serializer(warehouses, many=True)
        return Response(serializer.data)
