from rest_framework import serializers

from kancraonewms.master.models import Menu


class MenuSerializer(serializers.ModelSerializer):
    """Serializer untuk Menu model"""

    parent_name = serializers.CharField(source="parent.name", read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            "id",
            "code",
            "name",
            "icon",
            "url",
            "parent",
            "parent_name",
            "order",
            "is_active",
            "module",
            "children",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_children(self, obj):
        """Get child menus"""
        children = obj.children.filter(is_active=True).order_by("order")
        return MenuListSerializer(children, many=True).data


class MenuListSerializer(serializers.ModelSerializer):
    """Serializer untuk list Menus (lebih ringan)"""

    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = Menu
        fields = [
            "id",
            "code",
            "name",
            "icon",
            "url",
            "parent",
            "parent_name",
            "order",
            "is_active",
            "module",
        ]


class MenuTreeSerializer(serializers.ModelSerializer):
    """Serializer untuk hierarchical menu tree"""

    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ["id", "code", "name", "icon", "url", "order", "module", "children"]

    def get_children(self, obj):
        """Get child menus recursively"""
        children = obj.children.filter(is_active=True).order_by("order")
        return MenuTreeSerializer(children, many=True).data
