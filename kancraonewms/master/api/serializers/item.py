from rest_framework import serializers

from kancraonewms.master.models import Item


class ItemSerializer(serializers.ModelSerializer):
    """Serializer untuk Item model"""

    class Meta:
        model = Item
        fields = [
            "id",
            "code",
            "name",
            "description",
            "unit",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ItemListSerializer(serializers.ModelSerializer):
    """Serializer untuk list Items (lebih ringan)"""

    class Meta:
        model = Item
        fields = ["id", "code", "name", "unit", "is_active"]
