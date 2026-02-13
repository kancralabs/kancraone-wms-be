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

from kancraonewms.organizations.api.serializers import CompanyListSerializer
from kancraonewms.organizations.api.serializers import CompanySerializer
from kancraonewms.organizations.models import Company


class CompanyViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet untuk Company model"""

    queryset = Company.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return CompanyListSerializer
        return CompanySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by active status
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # Filter by company type
        company_type = self.request.query_params.get("company_type")
        if company_type:
            queryset = queryset.filter(company_type=company_type)

        # Filter by country
        country = self.request.query_params.get("country")
        if country:
            queryset = queryset.filter(country__iexact=country)

        # Search by code, name, or city
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(legal_name__icontains=search)
                | Q(city__icontains=search),
            )

        return queryset

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a company"""
        company = self.get_object()
        company.is_active = True
        company.save()
        serializer = self.get_serializer(company)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a company"""
        company = self.get_object()
        company.is_active = False
        company.save()
        serializer = self.get_serializer(company)
        return Response(serializer.data)
