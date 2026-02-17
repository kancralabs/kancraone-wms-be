from rest_framework import serializers

from kancraonewms.master.models import Accessibility


class AccessibilitySerializer(serializers.ModelSerializer):
    """Serializer untuk Accessibility model"""

    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = Accessibility
        fields = [
            "id",
            "role",
            "role_name",
            "module",
            "feature",
            "permission",
            "is_granted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AccessibilityListSerializer(serializers.ModelSerializer):
    """Serializer untuk list Accessibilities (lebih ringan)"""

    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = Accessibility
        fields = [
            "id",
            "role",
            "role_name",
            "module",
            "feature",
            "permission",
            "is_granted",
        ]
