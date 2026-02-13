from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Company


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
        self.message_user(request, _(f"{updated} companies activated successfully."))

    @admin.action(description=_("Deactivate selected companies"))
    def deactivate_companies(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} companies deactivated successfully."))

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
