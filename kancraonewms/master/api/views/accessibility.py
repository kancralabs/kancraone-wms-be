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

from kancraonewms.master.api.serializers import AccessibilityListSerializer
from kancraonewms.master.api.serializers import AccessibilitySerializer
from kancraonewms.master.models import Accessibility


class AccessibilityViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet untuk Accessibility model"""

    queryset = Accessibility.objects.select_related("role").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return AccessibilityListSerializer
        return AccessibilitySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", None)

        if search:
            queryset = queryset.filter(
                Q(role__name__icontains=search)
                | Q(module__icontains=search)
                | Q(feature__icontains=search),
            )

        role_id = self.request.query_params.get("role", None)
        if role_id:
            queryset = queryset.filter(role_id=role_id)

        module = self.request.query_params.get("module", None)
        if module:
            queryset = queryset.filter(module__icontains=module)

        permission = self.request.query_params.get("permission", None)
        if permission:
            queryset = queryset.filter(permission=permission)

        is_granted = self.request.query_params.get("is_granted", None)
        if is_granted is not None:
            queryset = queryset.filter(is_granted=is_granted.lower() == "true")

        return queryset.order_by("role", "module", "feature", "permission")

    @action(detail=False, methods=["get"])
    def by_role(self, request):
        """Get accessibilities by role"""
        role_id = request.query_params.get("role_id")
        if not role_id:
            return Response({"error": "role_id is required"}, status=400)

        accessibilities = self.get_queryset().filter(role_id=role_id)
        serializer = self.get_serializer(accessibilities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def grant(self, request, pk=None):
        """Grant permission"""
        accessibility = self.get_object()
        accessibility.is_granted = True
        accessibility.save()
        serializer = self.get_serializer(accessibility)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        """Revoke permission"""
        accessibility = self.get_object()
        accessibility.is_granted = False
        accessibility.save()
        serializer = self.get_serializer(accessibility)
        return Response(serializer.data)
