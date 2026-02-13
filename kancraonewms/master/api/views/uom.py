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

from kancraonewms.master.api.serializers import UOMListSerializer
from kancraonewms.master.api.serializers import UOMSerializer
from kancraonewms.master.models import UOM


class UOMViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet untuk UOM model"""

    queryset = UOM.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return UOMListSerializer
        return UOMSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by active status
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # Filter by UOM type
        uom_type = self.request.query_params.get("uom_type")
        if uom_type:
            queryset = queryset.filter(uom_type=uom_type)

        # Search by code or name
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) | Q(name__icontains=search),
            )

        return queryset

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a UOM"""
        uom = self.get_object()
        uom.is_active = True
        uom.save()
        serializer = self.get_serializer(uom)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a UOM"""
        uom = self.get_object()
        uom.is_active = False
        uom.save()
        serializer = self.get_serializer(uom)
        return Response(serializer.data)
