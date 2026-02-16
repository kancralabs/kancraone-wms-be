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

from kancraonewms.master.api.serializers.rack import RackCreateUpdateSerializer
from kancraonewms.master.api.serializers.rack import RackListSerializer
from kancraonewms.master.api.serializers.rack import RackSerializer
from kancraonewms.master.models import Rack


class RackViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet untuk Rack model"""

    queryset = Rack.objects.select_related("warehouse").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return RackListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return RackCreateUpdateSerializer
        return RackSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by warehouse
        warehouse_id = self.request.query_params.get("warehouse")
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)

        # Filter by active status
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # Filter by zone
        zone = self.request.query_params.get("zone")
        if zone:
            queryset = queryset.filter(zone__icontains=zone)

        # Filter by aisle
        aisle = self.request.query_params.get("aisle")
        if aisle:
            queryset = queryset.filter(aisle__icontains=aisle)

        # Search by code, name, zone, aisle, bay, or level
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(zone__icontains=search)
                | Q(aisle__icontains=search)
                | Q(bay__icontains=search)
                | Q(level__icontains=search),
            )

        return queryset

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a rack"""
        rack = self.get_object()
        rack.is_active = True
        rack.save()
        serializer = self.get_serializer(rack)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a rack"""
        rack = self.get_object()
        rack.is_active = False
        rack.save()
        serializer = self.get_serializer(rack)
        return Response(serializer.data)
