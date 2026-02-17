from django.contrib import admin  # pyright: ignore[reportMissingModuleSource]
from django.utils.translation import gettext_lazy as _  # type: ignore  # noqa: PGH003

from .models import UOM
from .models import Accessibility
from .models import Item
from .models import ItemUOM
from .models import Menu
from .models import Rack
from .models import Role
from .models import RoleMenuAccess


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
    list_display_links = ["code", "name"]
    list_filter = ["is_active", "created_at", "updated_at"]
    search_fields = ["code", "name", "description"]
    ordering = ["code"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 50
    inlines = [ItemUOMInline]
    actions = ["activate_items", "deactivate_items"]

    @admin.action(description=_("Activate selected items"))
    def activate_items(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} items activated successfully."))  # noqa: INT001

    @admin.action(description=_("Deactivate selected items"))
    def deactivate_items(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} items deactivated successfully."))  # noqa: INT001

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("code", "name", "description"),
            },
        ),
        (
            _("Details"),
            {
                "fields": ("unit", "is_active"),
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
    list_display_links = ["code", "name"]
    list_filter = ["uom_type", "is_active", "created_at", "updated_at"]
    search_fields = ["code", "name", "description"]
    ordering = ["code"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 50
    actions = ["activate_uoms", "deactivate_uoms"]

    @admin.action(description=_("Activate selected UOMs"))
    def activate_uoms(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} UOMs activated successfully."))  # noqa: INT001

    @admin.action(description=_("Deactivate selected UOMs"))
    def deactivate_uoms(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} UOMs deactivated successfully."))  # noqa: INT001

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("code", "name", "description"),
            },
        ),
        (
            _("Details"),
            {
                "fields": ("uom_type", "conversion_factor", "base_uom", "is_active"),
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
    list_display_links = ["item", "uom"]
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
    list_per_page = 50
    actions = ["activate_item_uoms", "deactivate_item_uoms", "set_as_base_uom"]

    @admin.action(description=_("Activate selected item UOMs"))
    def activate_item_uoms(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} item UOMs activated successfully."))  # noqa: INT001

    @admin.action(description=_("Deactivate selected item UOMs"))
    def deactivate_item_uoms(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} item UOMs deactivated successfully."))  # noqa: INT001

    @admin.action(description=_("Set as base UOM"))
    def set_as_base_uom(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                _("Please select only one item UOM to set as base."),
                level="error",
            )
            return
        item_uom = queryset.first()
        item_uom.is_base_uom = True
        item_uom.save()
        self.message_user(request, _(f"{item_uom} set as base UOM successfully."))  # noqa: INT001

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("item", "uom", "conversion_factor"),
            },
        ),
        (
            _("UOM Usage"),
            {
                "fields": (
                    "is_base_uom",
                    "is_purchase_uom",
                    "is_sales_uom",
                    "is_stock_uom",
                ),
            },
        ),
        (
            _("Additional Info"),
            {
                "fields": ("barcode", "is_active"),
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


@admin.register(Rack)
class RackAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "warehouse",
        "zone",
        "aisle",
        "bay",
        "level",
        "is_active",
        "created_at",
    ]
    list_display_links = ["code", "name"]
    list_filter = ["is_active", "warehouse", "zone", "created_at"]
    search_fields = ["code", "name", "zone", "aisle", "bay", "level"]
    ordering = ["warehouse", "code"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 50
    autocomplete_fields = ["warehouse"]
    actions = ["activate_racks", "deactivate_racks"]

    @admin.action(description=_("Activate selected racks"))
    def activate_racks(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} racks activated successfully."))  # noqa: INT001

    @admin.action(description=_("Deactivate selected racks"))
    def deactivate_racks(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} racks deactivated successfully."))  # noqa: INT001

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("warehouse", "code", "name", "description"),
            },
        ),
        (
            _("Location within Warehouse"),
            {
                "fields": ("zone", "aisle", "bay", "level"),
            },
        ),
        (
            _("Capacity"),
            {
                "fields": ("capacity", "max_weight"),
            },
        ),
        (
            _("Status"),
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


class AccessibilityInline(admin.TabularInline):
    model = Accessibility
    extra = 1
    fields = ["module", "feature", "permission", "is_granted"]
    list_display = ["module", "feature", "permission", "is_granted"]


class RoleMenuAccessInline(admin.TabularInline):
    model = RoleMenuAccess
    extra = 1
    fields = ["menu", "can_access"]
    autocomplete_fields = ["menu"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_active", "created_at", "updated_at"]
    list_display_links = ["code", "name"]
    list_filter = ["is_active", "created_at", "updated_at"]
    search_fields = ["code", "name", "description"]
    ordering = ["name"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 50
    inlines = [AccessibilityInline, RoleMenuAccessInline]
    actions = ["activate_roles", "deactivate_roles"]

    @admin.action(description=_("Activate selected roles"))
    def activate_roles(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} roles activated successfully."))  # noqa: INT001

    @admin.action(description=_("Deactivate selected roles"))
    def deactivate_roles(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} roles deactivated successfully."))  # noqa: INT001

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("code", "name", "description"),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("is_active",),
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


@admin.register(Accessibility)
class AccessibilityAdmin(admin.ModelAdmin):
    list_display = [
        "role",
        "module",
        "feature",
        "permission",
        "is_granted",
        "created_at",
    ]
    list_display_links = ["role", "module", "feature"]
    list_filter = ["permission", "is_granted", "module", "created_at"]
    search_fields = ["role__name", "module", "feature"]
    ordering = ["role", "module", "feature", "permission"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["role"]
    list_per_page = 50
    actions = ["grant_permission", "revoke_permission"]

    @admin.action(description=_("Grant permission"))
    def grant_permission(self, request, queryset):
        updated = queryset.update(is_granted=True)
        self.message_user(request, _(f"{updated} permissions granted successfully."))  # noqa: INT001

    @admin.action(description=_("Revoke permission"))
    def revoke_permission(self, request, queryset):
        updated = queryset.update(is_granted=False)
        self.message_user(request, _(f"{updated} permissions revoked successfully."))  # noqa: INT001

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("role", "module", "feature", "permission"),
            },
        ),
        (
            _("Access Control"),
            {
                "fields": ("is_granted",),
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


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "parent",
        "module",
        "order",
        "is_active",
        "created_at",
    ]
    list_display_links = ["code", "name"]
    list_filter = ["is_active", "module", "created_at"]
    search_fields = ["code", "name", "url", "module"]
    ordering = ["order", "name"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["parent"]
    list_per_page = 50
    actions = ["activate_menus", "deactivate_menus"]

    @admin.action(description=_("Activate selected menus"))
    def activate_menus(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} menus activated successfully."))  # noqa: INT001

    @admin.action(description=_("Deactivate selected menus"))
    def deactivate_menus(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} menus deactivated successfully."))  # noqa: INT001

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("code", "name", "icon", "url", "module"),
            },
        ),
        (
            _("Hierarchy"),
            {
                "fields": ("parent", "order"),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("is_active",),
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


@admin.register(RoleMenuAccess)
class RoleMenuAccessAdmin(admin.ModelAdmin):
    list_display = ["role", "menu", "can_access", "created_at"]
    list_display_links = ["role", "menu"]
    list_filter = ["can_access", "created_at"]
    search_fields = ["role__name", "menu__name", "menu__code"]
    ordering = ["role", "menu"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["role", "menu"]
    list_per_page = 50
    actions = ["grant_access", "revoke_access"]

    @admin.action(description=_("Grant access"))
    def grant_access(self, request, queryset):
        updated = queryset.update(can_access=True)
        self.message_user(request, _(f"{updated} accesses granted successfully."))  # noqa: INT001

    @admin.action(description=_("Revoke access"))
    def revoke_access(self, request, queryset):
        updated = queryset.update(can_access=False)
        self.message_user(request, _(f"{updated} accesses revoked successfully."))  # noqa: INT001

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("role", "menu"),
            },
        ),
        (
            _("Access Control"),
            {
                "fields": ("can_access",),
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
