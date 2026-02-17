from django.db import models  # pyright: ignore[reportMissingModuleSource]  # noqa: I001
from django.utils.translation import gettext_lazy as _  # pyright: ignore[reportMissingModuleSource]


class Role(models.Model):
    """Model untuk master roles/peran pengguna"""

    name = models.CharField(
        _("Role Name"),
        max_length=100,
        unique=True,
        help_text=_("Unique name for the role"),
    )
    code = models.CharField(
        _("Role Code"),
        max_length=50,
        unique=True,
        help_text=_("Unique code for the role"),
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Detailed description of the role"),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Whether this role is active"),
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
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        ordering = ["name"]
        db_table = "master_role"

    def __str__(self):
        return self.name
