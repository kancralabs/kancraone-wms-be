from rest_framework import serializers

from kancraonewms.master.models import RoleMenuAccess


class RoleMenuAccessSerializer(serializers.ModelSerializer):
    """Serializer untuk RoleMenuAccess model"""

    role_name = serializers.CharField(source="role.name", read_only=True)
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    menu_code = serializers.CharField(source="menu.code", read_only=True)

    class Meta:
        model = RoleMenuAccess
        fields = [
            "id",
            "role",
            "role_name",
            "menu",
            "menu_name",
            "menu_code",
            "can_access",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoleMenuAccessListSerializer(serializers.ModelSerializer):
    """Serializer untuk list RoleMenuAccesses (lebih ringan)"""

    role_name = serializers.CharField(source="role.name", read_only=True)
    menu_name = serializers.CharField(source="menu.name", read_only=True)

    class Meta:
        model = RoleMenuAccess
        fields = ["id", "role", "role_name", "menu", "menu_name", "can_access"]
