from rest_framework import serializers

from kancraonewms.master.models import Role


class RoleSerializer(serializers.ModelSerializer):
    """Serializer untuk Role model"""

    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoleListSerializer(serializers.ModelSerializer):
    """Serializer untuk list Roles (lebih ringan)"""

    class Meta:
        model = Role
        fields = ["id", "code", "name", "is_active"]
