from django.db import models
from django.utils.translation import gettext_lazy as _


class ItemUOM(models.Model):
    """Model untuk Item UOM Conversion"""

    item = models.ForeignKey(
        "Item",
        on_delete=models.CASCADE,
        related_name="item_uoms",
        verbose_name=_("Item"),
    )
    uom = models.ForeignKey(
        "UOM",
        on_delete=models.PROTECT,
        related_name="item_uoms",
        verbose_name=_("Unit of Measure"),
    )
    conversion_factor = models.DecimalField(
        _("Conversion Factor"),
        max_digits=10,
        decimal_places=4,
        default=1.0,
        help_text=_("Conversion factor from base UOM"),
    )
    is_base_uom = models.BooleanField(
        _("Is Base UOM"),
        default=False,
        help_text=_("Is this the base/default unit for this item"),
    )
    is_purchase_uom = models.BooleanField(
        _("Is Purchase UOM"),
        default=False,
        help_text=_("Can be used for purchasing"),
    )
    is_sales_uom = models.BooleanField(
        _("Is Sales UOM"),
        default=False,
        help_text=_("Can be used for sales"),
    )
    is_stock_uom = models.BooleanField(
        _("Is Stock UOM"),
        default=False,
        help_text=_("Can be used for stock/inventory"),
    )
    barcode = models.CharField(
        _("Barcode"),
        max_length=100,
        blank=True,
        help_text=_("Barcode for this item-UOM combination"),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Whether this item-UOM is currently active"),
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
        verbose_name = _("Item UOM")
        verbose_name_plural = _("Item UOMs")
        ordering = ["item", "uom"]
        unique_together = [["item", "uom"]]
        indexes = [
            models.Index(fields=["item", "uom"]),
            models.Index(fields=["item", "is_base_uom"]),
            models.Index(fields=["barcode"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.item.code} - {self.uom.code} (x{self.conversion_factor})"

    def save(self, *args, **kwargs):
        """Ensure only one base UOM per item"""
        if self.is_base_uom:
            # Set all other UOMs for this item to non-base
            ItemUOM.objects.filter(item=self.item, is_base_uom=True).exclude(
                pk=self.pk,
            ).update(is_base_uom=False)
        super().save(*args, **kwargs)
