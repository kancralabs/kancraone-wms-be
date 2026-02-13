from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from .models import Item


class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = "master/item_list.html"
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(code__icontains=search) |  # noqa: F821
                models.Q(name__icontains=search),  # noqa: F821
            )
        return queryset


class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = "master/item_detail.html"
    context_object_name = "item"


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    template_name = "master/item_form.html"
    fields = ["code", "name", "description", "unit", "is_active"]
    success_url = reverse_lazy("master:item-list")


class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    template_name = "master/item_form.html"
    fields = ["code", "name", "description", "unit", "is_active"]
    success_url = reverse_lazy("master:item-list")


class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Item
    template_name = "master/item_confirm_delete.html"
    success_url = reverse_lazy("master:item-list")
