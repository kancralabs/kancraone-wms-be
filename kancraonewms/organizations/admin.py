from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Company
from .models import Warehouse


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "company_type",
        "city",
        "country",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_display_links = ["code", "name"]
    list_filter = ["company_type", "is_active", "country", "created_at", "updated_at"]
    search_fields = ["code", "name", "legal_name", "city", "tax_id", "email"]
    ordering = ["code"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 50
    actions = ["activate_companies", "deactivate_companies"]

    @admin.action(description=_("Activate selected companies"))
    def activate_companies(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} companies activated successfully."))  # noqa: INT001

    @admin.action(description=_("Deactivate selected companies"))
    def deactivate_companies(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} companies deactivated successfully."))  # noqa: INT001

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("code", "name", "legal_name", "company_type", "tax_id"),
            },
        ),
        (
            _("Contact Information"),
            {
                "fields": ("phone", "email", "website"),
            },
        ),
        (
            _("Address"),
            {
                "fields": ("address", "city", "state", "postal_code", "country"),
            },
        ),
        (
            _("Business Details"),
            {
                "fields": ("currency", "payment_terms", "credit_limit"),
            },
        ),
        (
            _("Additional Information"),
            {
                "fields": ("is_active", "notes"),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "company",
        "city",
        "country",
        "is_active",
        "is_default",
        "created_at",
    ]
    list_display_links = ["code", "name"]
    list_filter = ["company", "is_active", "is_default", "country", "created_at"]
    search_fields = ["code", "name", "company__name", "city", "address_line1"]
    ordering = ["company", "code"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 50
    actions = ["activate_warehouses", "deactivate_warehouses"]
    autocomplete_fields = ["company"]

    @admin.action(description=_("Activate selected warehouses"))
    def activate_warehouses(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} warehouses activated successfully."))  # noqa: INT001

    @admin.action(description=_("Deactivate selected warehouses"))
    def deactivate_warehouses(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} warehouses deactivated successfully."))  # noqa: INT001

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("company", "code", "name", "description"),
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    "city",
                    "state",
                    "postal_code",
                    "country",
                ),
            },
        ),
        (
            _("Contact Information"),
            {
                "fields": ("phone", "email"),
            },
        ),
        (
            _("Settings"),
            {
                "fields": ("is_active", "is_default"),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
