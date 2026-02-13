from rest_framework import serializers

from kancraonewms.organizations.models import Company


class CompanySerializer(serializers.ModelSerializer):
    """Serializer untuk Company model"""

    class Meta:
        model = Company
        fields = [
            "id",
            "code",
            "name",
            "legal_name",
            "company_type",
            "tax_id",
            "phone",
            "email",
            "website",
            "address",
            "city",
            "state",
            "postal_code",
            "country",
            "currency",
            "payment_terms",
            "credit_limit",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CompanyListSerializer(serializers.ModelSerializer):
    """Serializer untuk list Companies (lebih ringan)"""

    class Meta:
        model = Company
        fields = [
            "id",
            "code",
            "name",
            "company_type",
            "city",
            "country",
            "is_active",
        ]
