from django.db import models  # pyright: ignore[reportMissingModuleSource]  # noqa: I001
from django.utils.translation import gettext_lazy as _  # pyright: ignore[reportMissingModuleSource]


class Menu(models.Model):
    """Model untuk master menu"""

    name = models.CharField(
        _("Menu Name"),
        max_length=100,
        help_text=_("Display name of the menu"),
    )
    code = models.CharField(
        _("Menu Code"),
        max_length=50,
        unique=True,
        help_text=_("Unique code for the menu"),
    )
    icon = models.CharField(
        _("Icon"),
        max_length=100,
        blank=True,
        help_text=_("Icon class or name for the menu"),
    )
    url = models.CharField(
        _("URL"),
        max_length=255,
        blank=True,
        help_text=_("URL path for the menu"),
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Parent Menu"),
        help_text=_("Parent menu for hierarchical structure"),
    )
    order = models.IntegerField(
        _("Order"),
        default=0,
        help_text=_("Display order of the menu"),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Whether this menu is active"),
    )
    module = models.CharField(
        _("Module"),
        max_length=100,
        blank=True,
        help_text=_("Module name (e.g., master, inventory, transaction)"),
    )
    created_at = models.DateTimeField(
        _("Created At"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Updated At"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("Menu")
        verbose_name_plural = _("Menus")
        ordering = ["order", "name"]
        db_table = "master_menu"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
