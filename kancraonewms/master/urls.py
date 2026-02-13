from django.urls import path

from .views import ItemCreateView
from .views import ItemDeleteView
from .views import ItemDetailView
from .views import ItemListView
from .views import ItemUOMCreateView
from .views import ItemUOMDeleteView
from .views import ItemUOMDetailView
from .views import ItemUOMListView
from .views import ItemUOMUpdateView
from .views import ItemUpdateView
from .views import UOMCreateView
from .views import UOMDeleteView
from .views import UOMDetailView
from .views import UOMListView
from .views import UOMUpdateView

app_name = "master"

urlpatterns = [
    # Item URLs
    path("items/", ItemListView.as_view(), name="item-list"),
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item-detail"),
    path("items/create/", ItemCreateView.as_view(), name="item-create"),
    path("items/<int:pk>/update/", ItemUpdateView.as_view(), name="item-update"),
    path("items/<int:pk>/delete/", ItemDeleteView.as_view(), name="item-delete"),
    # UOM URLs
    path("uoms/", UOMListView.as_view(), name="uom-list"),
    path("uoms/<int:pk>/", UOMDetailView.as_view(), name="uom-detail"),
    path("uoms/create/", UOMCreateView.as_view(), name="uom-create"),
    path("uoms/<int:pk>/update/", UOMUpdateView.as_view(), name="uom-update"),
    path("uoms/<int:pk>/delete/", UOMDeleteView.as_view(), name="uom-delete"),
    # ItemUOM URLs
    path("item-uoms/", ItemUOMListView.as_view(), name="item-uom-list"),
    path("item-uoms/<int:pk>/", ItemUOMDetailView.as_view(), name="item-uom-detail"),
    path("item-uoms/create/", ItemUOMCreateView.as_view(), name="item-uom-create"),
    path(
        "item-uoms/<int:pk>/update/",
        ItemUOMUpdateView.as_view(),
        name="item-uom-update",
    ),
    path(
        "item-uoms/<int:pk>/delete/",
        ItemUOMDeleteView.as_view(),
        name="item-uom-delete",
    ),
]
