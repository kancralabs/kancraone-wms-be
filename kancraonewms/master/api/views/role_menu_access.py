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

from kancraonewms.master.api.serializers import RoleMenuAccessListSerializer
from kancraonewms.master.api.serializers import RoleMenuAccessSerializer
from kancraonewms.master.models import RoleMenuAccess


class RoleMenuAccessViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet untuk RoleMenuAccess model"""

    queryset = RoleMenuAccess.objects.select_related("role", "menu").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return RoleMenuAccessListSerializer
        return RoleMenuAccessSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", None)

        if search:
            queryset = queryset.filter(
                Q(role__name__icontains=search)
                | Q(menu__name__icontains=search)
                | Q(menu__code__icontains=search),
            )

        role_id = self.request.query_params.get("role", None)
        if role_id:
            queryset = queryset.filter(role_id=role_id)

        menu_id = self.request.query_params.get("menu", None)
        if menu_id:
            queryset = queryset.filter(menu_id=menu_id)

        can_access = self.request.query_params.get("can_access", None)
        if can_access is not None:
            queryset = queryset.filter(can_access=can_access.lower() == "true")

        return queryset.order_by("role", "menu")

    @action(detail=False, methods=["get"])
    def by_role(self, request):
        """Get menu accesses by role"""
        role_id = request.query_params.get("role_id")
        if not role_id:
            return Response({"error": "role_id is required"}, status=400)

        accesses = self.get_queryset().filter(role_id=role_id, can_access=True)
        serializer = self.get_serializer(accesses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def accessible_menus(self, request):
        """Get accessible menus for a role"""
        role_id = request.query_params.get("role_id")
        if not role_id:
            return Response({"error": "role_id is required"}, status=400)

        from kancraonewms.master.api.serializers import MenuTreeSerializer  # noqa: I001, PLC0415

        accesses = self.get_queryset().filter(
            role_id=role_id,
            can_access=True,
            menu__is_active=True,
        )
        menus = [access.menu for access in accesses if access.menu.parent is None]
        serializer = MenuTreeSerializer(menus, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def grant(self, request, pk=None):
        """Grant access to menu"""
        access = self.get_object()
        access.can_access = True
        access.save()
        serializer = self.get_serializer(access)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        """Revoke access to menu"""
        access = self.get_object()
        access.can_access = False
        access.save()
        serializer = self.get_serializer(access)
        return Response(serializer.data)
