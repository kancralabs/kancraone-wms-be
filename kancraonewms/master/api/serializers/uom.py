from rest_framework import serializers

from kancraonewms.master.models import UOM


class UOMSerializer(serializers.ModelSerializer):
    """Serializer untuk UOM model"""

    base_uom_code = serializers.CharField(source="base_uom.code", read_only=True)
    base_uom_name = serializers.CharField(source="base_uom.name", read_only=True)

    class Meta:
        model = UOM
        fields = [
            "id",
            "code",
            "name",
            "description",
            "uom_type",
            "conversion_factor",
            "base_uom",
            "base_uom_code",
            "base_uom_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UOMListSerializer(serializers.ModelSerializer):
    """Serializer untuk list UOMs (lebih ringan)"""

    class Meta:
        model = UOM
        fields = ["id", "code", "name", "uom_type", "is_active"]
