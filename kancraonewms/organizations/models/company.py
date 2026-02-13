from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    """Model untuk Company/Organization"""

    COMPANY_TYPE_CHOICES = [
        ("own", _("Own Company")),
        ("customer", _("Customer")),
        ("vendor", _("Vendor")),
        ("both", _("Customer & Vendor")),
    ]

    code = models.CharField(
        _("Company Code"),
        max_length=50,
        unique=True,
        help_text=_("Unique code for the company"),
    )
    name = models.CharField(
        _("Company Name"),
        max_length=255,
        help_text=_("Name of the company"),
    )
    legal_name = models.CharField(
        _("Legal Name"),
        max_length=255,
        blank=True,
        help_text=_("Official legal name of the company"),
    )
    company_type = models.CharField(
        _("Company Type"),
        max_length=20,
        choices=COMPANY_TYPE_CHOICES,
        default="customer",
        help_text=_("Type of company relationship"),
    )
    tax_id = models.CharField(
        _("Tax ID/NPWP"),
        max_length=50,
        blank=True,
        help_text=_("Tax identification number"),
    )
    
    # Contact Information
    phone = models.CharField(
        _("Phone"),
        max_length=50,
        blank=True,
    )
    email = models.EmailField(
        _("Email"),
        blank=True,
    )
    website = models.URLField(
        _("Website"),
        blank=True,
    )
    
    # Address
    address = models.TextField(
        _("Address"),
        blank=True,
    )
    city = models.CharField(
        _("City"),
        max_length=100,
        blank=True,
    )
    state = models.CharField(
        _("State/Province"),
        max_length=100,
        blank=True,
    )
    postal_code = models.CharField(
        _("Postal Code"),
        max_length=20,
        blank=True,
    )
    country = models.CharField(
        _("Country"),
        max_length=100,
        default="Indonesia",
    )
    
    # Business Details
    currency = models.CharField(
        _("Currency"),
        max_length=10,
        default="IDR",
        help_text=_("Default currency for transactions"),
    )
    payment_terms = models.IntegerField(
        _("Payment Terms (Days)"),
        default=30,
        help_text=_("Default payment terms in days"),
    )
    credit_limit = models.DecimalField(
        _("Credit Limit"),
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text=_("Credit limit for this company"),
    )
    
    # Status
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Whether this company is currently active"),
    )
    notes = models.TextField(
        _("Notes"),
        blank=True,
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
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["name"]),
            models.Index(fields=["company_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
