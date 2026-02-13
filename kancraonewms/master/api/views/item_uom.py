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

from kancraonewms.master.api.serializers import ItemUOMListSerializer
from kancraonewms.master.api.serializers import ItemUOMSerializer
from kancraonewms.master.models import ItemUOM


class ItemUOMViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet untuk ItemUOM model"""

    queryset = ItemUOM.objects.select_related("item", "uom").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ItemUOMListSerializer
        return ItemUOMSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by active status
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # Filter by item
        item_id = self.request.query_params.get("item")
        if item_id:
            queryset = queryset.filter(item_id=item_id)

        # Filter by UOM
        uom_id = self.request.query_params.get("uom")
        if uom_id:
            queryset = queryset.filter(uom_id=uom_id)

        # Filter by base UOM
        is_base_uom = self.request.query_params.get("is_base_uom")
        if is_base_uom is not None:
            queryset = queryset.filter(is_base_uom=is_base_uom.lower() == "true")

        # Filter by purchase UOM
        is_purchase_uom = self.request.query_params.get("is_purchase_uom")
        if is_purchase_uom is not None:
            queryset = queryset.filter(
                is_purchase_uom=is_purchase_uom.lower() == "true",
            )

        # Filter by sales UOM
        is_sales_uom = self.request.query_params.get("is_sales_uom")
        if is_sales_uom is not None:
            queryset = queryset.filter(is_sales_uom=is_sales_uom.lower() == "true")

        # Filter by stock UOM
        is_stock_uom = self.request.query_params.get("is_stock_uom")
        if is_stock_uom is not None:
            queryset = queryset.filter(is_stock_uom=is_stock_uom.lower() == "true")

        # Search by barcode or item/uom codes
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(barcode__icontains=search)
                | Q(item__code__icontains=search)
                | Q(item__name__icontains=search)
                | Q(uom__code__icontains=search)
                | Q(uom__name__icontains=search),
            )

        return queryset

    @action(detail=True, methods=["post"])
    def set_as_base(self, request, pk=None):
        """Set this item-UOM as base UOM for the item"""
        item_uom = self.get_object()
        item_uom.is_base_uom = True
        item_uom.save()
        serializer = self.get_serializer(item_uom)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate an item-UOM"""
        item_uom = self.get_object()
        item_uom.is_active = True
        item_uom.save()
        serializer = self.get_serializer(item_uom)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate an item-UOM"""
        item_uom = self.get_object()
        item_uom.is_active = False
        item_uom.save()
        serializer = self.get_serializer(item_uom)
        return Response(serializer.data)
