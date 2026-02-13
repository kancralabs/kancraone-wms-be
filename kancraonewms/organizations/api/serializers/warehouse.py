from rest_framework import serializers

from kancraonewms.organizations.models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    """Serializer untuk Warehouse model"""

    company_name = serializers.CharField(source="company.name", read_only=True)
    company_code = serializers.CharField(source="company.code", read_only=True)

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "company",
            "company_name",
            "company_code",
            "code",
            "name",
            "description",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "phone",
            "email",
            "is_active",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WarehouseListSerializer(serializers.ModelSerializer):
    """Serializer untuk list Warehouses (lebih ringan)"""

    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "code",
            "name",
            "company",
            "company_name",
            "city",
            "country",
            "is_active",
            "is_default",
        ]


class WarehouseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer untuk create/update Warehouse dengan validasi"""

    class Meta:
        model = Warehouse
        fields = [
            "company",
            "code",
            "name",
            "description",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "phone",
            "email",
            "is_active",
            "is_default",
        ]

    def validate_code(self, value):
        """Validasi uniqueness code"""
        instance = self.instance
        if instance:
            # Update case - exclude current instance
            if Warehouse.objects.exclude(pk=instance.pk).filter(code=value).exists():
                msg = "Warehouse code already exists."
                raise serializers.ValidationError(msg)
        # Create case
        elif Warehouse.objects.filter(code=value).exists():
            msg = "Warehouse code already exists."
            raise serializers.ValidationError(msg)
        return value

    def validate(self, attrs):
        """Additional validation"""
        # Ensure company is provided
        if "company" not in attrs and not self.instance:
            raise serializers.ValidationError({"company": "Company is required."})

        return attrs
