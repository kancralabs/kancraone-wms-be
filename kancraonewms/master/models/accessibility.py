from django.db import models  # pyright: ignore[reportMissingModuleSource]  # noqa: I001
from django.utils.translation import gettext_lazy as _  # pyright: ignore[reportMissingModuleSource]

from .role import Role


class Accessibility(models.Model):
    """Model untuk accessibility/hak akses per role"""

    PERMISSION_CHOICES = [
        ("create", _("Create")),
        ("read", _("Read")),
        ("update", _("Update")),
        ("delete", _("Delete")),
        ("export", _("Export")),
        ("import", _("Import")),
    ]

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="accessibilities",
        verbose_name=_("Role"),
        help_text=_("Role that has this accessibility"),
    )
    module = models.CharField(
        _("Module"),
        max_length=100,
        help_text=_("Module name (e.g., master, inventory, transaction)"),
    )
    feature = models.CharField(
        _("Feature"),
        max_length=100,
        help_text=_("Feature name (e.g., item, uom, rack)"),
    )
    permission = models.CharField(
        _("Permission"),
        max_length=20,
        choices=PERMISSION_CHOICES,
        help_text=_("Permission type"),
    )
    is_granted = models.BooleanField(
        _("Is Granted"),
        default=True,
        help_text=_("Whether this permission is granted"),
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
        verbose_name = _("Accessibility")
        verbose_name_plural = _("Accessibilities")
        ordering = ["role", "module", "feature", "permission"]
        db_table = "master_accessibility"
        unique_together = [["role", "module", "feature", "permission"]]

    def __str__(self):
        return f"{self.role.name} - {self.module}.{self.feature}.{self.permission}"
