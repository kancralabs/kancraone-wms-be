from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from kancraonewms.master.api.views import ItemViewSet, UOMViewSet
from kancraonewms.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("items", ItemViewSet)
router.register("uoms", UOMViewSet)


app_name = "api"
urlpatterns = router.urls
