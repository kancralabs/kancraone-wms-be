from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from kancraonewms.master.api.views import AccessibilityViewSet
from kancraonewms.master.api.views import ItemUOMViewSet
from kancraonewms.master.api.views import ItemViewSet
from kancraonewms.master.api.views import MenuViewSet
from kancraonewms.master.api.views import RackViewSet
from kancraonewms.master.api.views import RoleMenuAccessViewSet
from kancraonewms.master.api.views import RoleViewSet
from kancraonewms.master.api.views import UOMViewSet
from kancraonewms.organizations.api.views import CompanyViewSet
from kancraonewms.organizations.api.views import WarehouseViewSet
from kancraonewms.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("companies", CompanyViewSet)
router.register("warehouses", WarehouseViewSet)
router.register("items", ItemViewSet)
router.register("uoms", UOMViewSet)
router.register("item-uoms", ItemUOMViewSet)
router.register("racks", RackViewSet)
router.register("roles", RoleViewSet)
router.register("accessibilities", AccessibilityViewSet)
router.register("menus", MenuViewSet)
router.register("role-menu-accesses", RoleMenuAccessViewSet)


app_name = "api"
urlpatterns = [  # noqa: RUF005
    # Auth endpoints
    path("auth/", include("kancraonewms.users.api.auth_urls")),
    # Router endpoints
] + router.urls
