from django.db import models
from django.utils.translation import gettext_lazy as _

from kancraonewms.organizations.models import Warehouse


class Rack(models.Model):
    """Model untuk Rack yang berada dalam Warehouse"""

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="racks",
        verbose_name=_("Warehouse"),
        help_text=_("Warehouse that contains this rack"),
    )
    code = models.CharField(
        _("Rack Code"),
        max_length=50,
        unique=True,
        help_text=_("Unique code for the rack"),
    )
    name = models.CharField(
        _("Rack Name"),
        max_length=255,
        help_text=_("Name of the rack"),
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Detailed description of the rack"),
    )

    # Location Information within Warehouse
    zone = models.CharField(
        _("Zone"),
        max_length=50,
        blank=True,
        help_text=_("Zone or area within the warehouse"),
    )
    aisle = models.CharField(
        _("Aisle"),
        max_length=50,
        blank=True,
        help_text=_("Aisle number or identifier"),
    )
    bay = models.CharField(
        _("Bay/Section"),
        max_length=50,
        blank=True,
        help_text=_("Bay or section identifier"),
    )
    level = models.CharField(
        _("Level"),
        max_length=50,
        blank=True,
        help_text=_("Level or shelf number"),
    )

    # Capacity Information
    capacity = models.DecimalField(
        _("Capacity"),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Storage capacity (cubic meters or other unit)"),
    )
    max_weight = models.DecimalField(
        _("Max Weight"),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Maximum weight capacity (kg)"),
    )

    # Status
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Whether this rack is currently active"),
    )
    notes = models.TextField(
        _("Notes"),
        blank=True,
        help_text=_("Additional notes about the rack"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Rack")
        verbose_name_plural = _("Racks")
        ordering = ["warehouse", "code"]
        indexes = [
            models.Index(fields=["warehouse", "code"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["zone", "aisle"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name} ({self.warehouse.name})"
