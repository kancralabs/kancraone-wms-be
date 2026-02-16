from rest_framework import serializers

from kancraonewms.master.models import Rack
from kancraonewms.organizations.api.serializers.warehouse import WarehouseListSerializer


class RackSerializer(serializers.ModelSerializer):
    """Serializer for Rack detail view"""

    warehouse_detail = WarehouseListSerializer(source="warehouse", read_only=True)

    class Meta:
        model = Rack
        fields = [
            "id",
            "warehouse",
            "warehouse_detail",
            "code",
            "name",
            "description",
            "zone",
            "aisle",
            "bay",
            "level",
            "capacity",
            "max_weight",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_code(self, value):
        """Validate that code is unique"""
        instance = self.instance
        if instance and instance.code == value:
            return value

        if Rack.objects.filter(code=value).exists():
            msg = "Rack with this code already exists."
            raise serializers.ValidationError(msg)
        return value


class RackListSerializer(serializers.ModelSerializer):
    """Serializer for Rack list view with limited fields"""

    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = Rack
        fields = [
            "id",
            "code",
            "name",
            "warehouse",
            "warehouse_name",
            "zone",
            "aisle",
            "bay",
            "level",
            "is_active",
        ]


class RackCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Rack"""

    class Meta:
        model = Rack
        fields = [
            "warehouse",
            "code",
            "name",
            "description",
            "zone",
            "aisle",
            "bay",
            "level",
            "capacity",
            "max_weight",
            "is_active",
            "notes",
        ]

    def validate_code(self, value):
        """Validate that code is unique"""
        instance = self.instance
        if instance and instance.code == value:
            return value

        if Rack.objects.filter(code=value).exists():
            msg = "Rack with this code already exists."
            raise serializers.ValidationError(msg)
        return value

    def validate_capacity(self, value):
        """Validate that capacity is not negative"""
        if value < 0:
            msg = "Capacity cannot be negative."
            raise serializers.ValidationError(msg)
        return value

    def validate_max_weight(self, value):
        """Validate that max weight is not negative"""
        if value < 0:
            msg = "Max weight cannot be negative."
            raise serializers.ValidationError(msg)
        return value
