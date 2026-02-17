from django.db import models  # pyright: ignore[reportMissingModuleSource]  # noqa: I001
from django.utils.translation import gettext_lazy as _  # pyright: ignore[reportMissingModuleSource]

from .menu import Menu
from .role import Role


class RoleMenuAccess(models.Model):
    """Model untuk menghubungkan role dengan menu yang bisa diakses"""

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="menu_accesses",
        verbose_name=_("Role"),
        help_text=_("Role that has access to the menu"),
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="role_accesses",
        verbose_name=_("Menu"),
        help_text=_("Menu that can be accessed"),
    )
    can_access = models.BooleanField(
        _("Can Access"),
        default=True,
        help_text=_("Whether the role can access this menu"),
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
        verbose_name = _("Role Menu Access")
        verbose_name_plural = _("Role Menu Accesses")
        ordering = ["role", "menu"]
        db_table = "master_role_menu_access"
        unique_together = [["role", "menu"]]

    def __str__(self):
        return f"{self.role.name} - {self.menu.name}"
