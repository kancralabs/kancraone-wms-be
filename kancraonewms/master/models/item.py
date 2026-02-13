from django.db import models
from django.utils.translation import gettext_lazy as _


class Item(models.Model):
    """Model untuk master items"""

    code = models.CharField(
        _("Item Code"),
        max_length=50,
        unique=True,
        help_text=_("Unique code for the item"),
    )
    name = models.CharField(
        _("Item Name"),
        max_length=255,
        help_text=_("Name of the item"),
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Detailed description of the item"),
    )
    unit = models.CharField(
        _("Unit"),
        max_length=50,
        help_text=_("Unit of measurement (e.g., pcs, kg, liter)"),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Whether this item is currently active"),
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
        verbose_name = _("Item")
        verbose_name_plural = _("Items")
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
