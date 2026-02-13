from django.db import models
from django.utils.translation import gettext_lazy as _

from .company import Company


class Warehouse(models.Model):
    """Model untuk Warehouse yang terhubung dengan Company"""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="warehouses",
        verbose_name=_("Company"),
        help_text=_("Company that owns this warehouse"),
    )
    code = models.CharField(
        _("Warehouse Code"),
        max_length=50,
        unique=True,
        help_text=_("Unique code for the warehouse"),
    )
    name = models.CharField(
        _("Warehouse Name"),
        max_length=255,
        help_text=_("Name of the warehouse"),
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Detailed description of the warehouse"),
    )

    # Address Information
    address_line1 = models.CharField(
        _("Address Line 1"),
        max_length=255,
        blank=True,
        help_text=_("Street address"),
    )
    address_line2 = models.CharField(
        _("Address Line 2"),
        max_length=255,
        blank=True,
        help_text=_("Additional address information"),
    )
    city = models.CharField(
        _("City"),
        max_length=100,
        blank=True,
        help_text=_("City name"),
    )
    state = models.CharField(
        _("State/Province"),
        max_length=100,
        blank=True,
        help_text=_("State or province name"),
    )
    postal_code = models.CharField(
        _("Postal Code"),
        max_length=20,
        blank=True,
        help_text=_("Postal/ZIP code"),
    )
    country = models.CharField(
        _("Country"),
        max_length=100,
        blank=True,
        default="Indonesia",
        help_text=_("Country name"),
    )

    # Contact Information
    phone = models.CharField(
        _("Phone"),
        max_length=50,
        blank=True,
        help_text=_("Contact phone number"),
    )
    email = models.EmailField(
        _("Email"),
        blank=True,
        help_text=_("Contact email address"),
    )

    # Warehouse Settings
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Whether this warehouse is currently active"),
    )
    is_default = models.BooleanField(
        _("Default Warehouse"),
        default=False,
        help_text=_("Whether this is the default warehouse for the company"),
    )

    # Timestamps
    created_at = models.DateTimeField(
        _("Created At"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Updated At"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("Warehouse")
        verbose_name_plural = _("Warehouses")
        ordering = ["company", "code"]
        indexes = [
            models.Index(fields=["company", "code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name} ({self.company.name})"

    def save(self, *args, **kwargs):
        """Override save to ensure only one default warehouse per company"""
        if self.is_default:
            # Set all other warehouses of the same company to non-default
            Warehouse.objects.filter(
                company=self.company,
                is_default=True,
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
