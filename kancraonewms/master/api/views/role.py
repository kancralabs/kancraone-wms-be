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

from kancraonewms.master.api.serializers import RoleListSerializer
from kancraonewms.master.api.serializers import RoleSerializer
from kancraonewms.master.models import Role


class RoleViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet untuk Role model"""

    queryset = Role.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return RoleListSerializer
        return RoleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", None)

        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(description__icontains=search),
            )

        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        return queryset.order_by("name")

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get only active roles"""
        active_roles = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_roles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a role"""
        role = self.get_object()
        role.is_active = True
        role.save()
        serializer = self.get_serializer(role)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a role"""
        role = self.get_object()
        role.is_active = False
        role.save()
        serializer = self.get_serializer(role)
        return Response(serializer.data)
