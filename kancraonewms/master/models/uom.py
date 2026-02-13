from django.db import models
from django.utils.translation import gettext_lazy as _


class UOM(models.Model):
    """Model untuk Unit of Measure (UOM)"""

    code = models.CharField(
        _("UOM Code"),
        max_length=20,
        unique=True,
        help_text=_("Unique code for the unit of measure"),
    )
    name = models.CharField(
        _("UOM Name"),
        max_length=100,
        help_text=_("Name of the unit of measure"),
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Detailed description of the UOM"),
    )
    uom_type = models.CharField(
        _("UOM Type"),
        max_length=50,
        choices=[
            ("weight", _("Weight")),
            ("length", _("Length")),
            ("volume", _("Volume")),
            ("quantity", _("Quantity")),
            ("time", _("Time")),
            ("other", _("Other")),
        ],
        default="quantity",
        help_text=_("Type/category of the unit"),
    )
    conversion_factor = models.DecimalField(
        _("Conversion Factor"),
        max_digits=10,
        decimal_places=4,
        default=1.0,
        help_text=_("Conversion factor to base unit"),
    )
    base_uom = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_uoms",
        verbose_name=_("Base UOM"),
        help_text=_("Reference base unit for conversion"),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Whether this UOM is currently active"),
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
        verbose_name = _("Unit of Measure")
        verbose_name_plural = _("Units of Measure")
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["name"]),
            models.Index(fields=["uom_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
