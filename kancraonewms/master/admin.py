from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import UOM
from .models import Item
from .models import ItemUOM


class ItemUOMInline(admin.TabularInline):
    model = ItemUOM
    extra = 1
    fields = [
        "uom",
        "conversion_factor",
        "is_base_uom",
        "is_purchase_uom",
        "is_sales_uom",
        "is_stock_uom",
        "barcode",
        "is_active",
    ]
    autocomplete_fields = ["uom"]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "unit", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active", "created_at", "updated_at"]
    search_fields = ["code", "name", "description"]
    ordering = ["code"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [ItemUOMInline]

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


@admin.register(UOM)
class UOMAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "uom_type",
        "conversion_factor",
        "base_uom",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = ["uom_type", "is_active", "created_at", "updated_at"]
    search_fields = ["code", "name", "description"]
    ordering = ["code"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (_("Basic Information"), {
            "fields": ("code", "name", "description"),
        }),
        (_("Details"), {
            "fields": ("uom_type", "conversion_factor", "base_uom", "is_active"),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(ItemUOM)
class ItemUOMAdmin(admin.ModelAdmin):
    list_display = [
        "item",
        "uom",
        "conversion_factor",
        "is_base_uom",
        "is_purchase_uom",
        "is_sales_uom",
        "is_stock_uom",
        "barcode",
        "is_active",
    ]
    list_filter = [
        "is_base_uom",
        "is_purchase_uom",
        "is_sales_uom",
        "is_stock_uom",
        "is_active",
    ]
    search_fields = ["item__code", "item__name", "uom__code", "uom__name", "barcode"]
    ordering = ["item", "uom"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["item", "uom"]

    fieldsets = (
        (_("Basic Information"), {
            "fields": ("item", "uom", "conversion_factor"),
        }),
        (_("UOM Usage"), {
            "fields": (
                "is_base_uom",
                "is_purchase_uom",
                "is_sales_uom",
                "is_stock_uom",
            ),
        }),
        (_("Additional Info"), {
            "fields": ("barcode", "is_active"),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

