from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "unit", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active", "created_at", "updated_at"]
    search_fields = ["code", "name", "description"]
    ordering = ["code"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (_("Basic Information"), {
            "fields": ("code", "name", "description"),
        }),
        (_("Details"), {
            "fields": ("unit", "is_active"),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
