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

from kancraonewms.master.api.serializers import MenuListSerializer
from kancraonewms.master.api.serializers import MenuSerializer
from kancraonewms.master.api.serializers import MenuTreeSerializer
from kancraonewms.master.models import Menu


class MenuViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet untuk Menu model"""

    queryset = Menu.objects.select_related("parent").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return MenuListSerializer
        if self.action == "tree":
            return MenuTreeSerializer
        return MenuSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", None)

        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(url__icontains=search)
                | Q(module__icontains=search),
            )

        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        module = self.request.query_params.get("module", None)
        if module:
            queryset = queryset.filter(module__icontains=module)

        parent_id = self.request.query_params.get("parent", None)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)

        return queryset.order_by("order", "name")

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get only active menus"""
        active_menus = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_menus, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """Get menu tree (hierarchical structure)"""
        # Get only parent menus (no parent)
        parent_menus = self.get_queryset().filter(parent__isnull=True, is_active=True)
        serializer = MenuTreeSerializer(parent_menus, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def roots(self, request):
        """Get root menus (menus without parent)"""
        root_menus = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(root_menus, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def children(self, request, pk=None):
        """Get children of a menu"""
        menu = self.get_object()
        children = menu.children.all()
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a menu"""
        menu = self.get_object()
        menu.is_active = True
        menu.save()
        serializer = self.get_serializer(menu)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a menu"""
        menu = self.get_object()
        menu.is_active = False
        menu.save()
        serializer = self.get_serializer(menu)
        return Response(serializer.data)
