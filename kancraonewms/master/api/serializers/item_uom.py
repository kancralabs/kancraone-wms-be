from rest_framework import serializers

from kancraonewms.master.models import ItemUOM


class ItemUOMSerializer(serializers.ModelSerializer):
    """Serializer untuk ItemUOM model"""

    item_code = serializers.CharField(source="item.code", read_only=True)
    item_name = serializers.CharField(source="item.name", read_only=True)
    uom_code = serializers.CharField(source="uom.code", read_only=True)
    uom_name = serializers.CharField(source="uom.name", read_only=True)

    class Meta:
        model = ItemUOM
        fields = [
            "id",
            "item",
            "item_code",
            "item_name",
            "uom",
            "uom_code",
            "uom_name",
            "conversion_factor",
            "is_base_uom",
            "is_purchase_uom",
            "is_sales_uom",
            "is_stock_uom",
            "barcode",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ItemUOMListSerializer(serializers.ModelSerializer):
    """Serializer untuk list ItemUOMs (lebih ringan)"""

    item_code = serializers.CharField(source="item.code", read_only=True)
    uom_code = serializers.CharField(source="uom.code", read_only=True)

    class Meta:
        model = ItemUOM
        fields = [
            "id",
            "item",
            "item_code",
            "uom",
            "uom_code",
            "conversion_factor",
            "is_base_uom",
            "is_active",
        ]
