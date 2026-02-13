from django.urls import path

from .views import ItemCreateView
from .views import ItemDeleteView
from .views import ItemDetailView
from .views import ItemListView
from .views import ItemUpdateView

app_name = "master"

urlpatterns = [
    path("items/", ItemListView.as_view(), name="item-list"),
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item-detail"),
    path("items/create/", ItemCreateView.as_view(), name="item-create"),
    path("items/<int:pk>/update/", ItemUpdateView.as_view(), name="item-update"),
    path("items/<int:pk>/delete/", ItemDeleteView.as_view(), name="item-delete"),
]
