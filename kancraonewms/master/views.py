from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from .models import UOM
from .models import Item
from .models import ItemUOM


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
                Q(code__icontains=search) | Q(name__icontains=search),
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


# UOM Views
class UOMListView(LoginRequiredMixin, ListView):
    model = UOM
    template_name = "master/uom_list.html"
    context_object_name = "uoms"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) | Q(name__icontains=search),
            )
        return queryset


class UOMDetailView(LoginRequiredMixin, DetailView):
    model = UOM
    template_name = "master/uom_detail.html"
    context_object_name = "uom"


class UOMCreateView(LoginRequiredMixin, CreateView):
    model = UOM
    template_name = "master/uom_form.html"
    fields = [
        "code",
        "name",
        "description",
        "uom_type",
        "conversion_factor",
        "base_uom",
        "is_active",
    ]
    success_url = reverse_lazy("master:uom-list")


class UOMUpdateView(LoginRequiredMixin, UpdateView):
    model = UOM
    template_name = "master/uom_form.html"
    fields = [
        "code",
        "name",
        "description",
        "uom_type",
        "conversion_factor",
        "base_uom",
        "is_active",
    ]
    success_url = reverse_lazy("master:uom-list")


class UOMDeleteView(LoginRequiredMixin, DeleteView):
    model = UOM
    template_name = "master/uom_confirm_delete.html"
    success_url = reverse_lazy("master:uom-list")


# ItemUOM Views
class ItemUOMListView(LoginRequiredMixin, ListView):
    model = ItemUOM
    template_name = "master/item_uom_list.html"
    context_object_name = "item_uoms"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related("item", "uom")
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(item__code__icontains=search)
                | Q(item__name__icontains=search)
                | Q(uom__code__icontains=search)
                | Q(uom__name__icontains=search)
                | Q(barcode__icontains=search),
            )
        return queryset


class ItemUOMDetailView(LoginRequiredMixin, DetailView):
    model = ItemUOM
    template_name = "master/item_uom_detail.html"
    context_object_name = "item_uom"


class ItemUOMCreateView(LoginRequiredMixin, CreateView):
    model = ItemUOM
    template_name = "master/item_uom_form.html"
    fields = [
        "item",
        "uom",
        "conversion_factor",
        "is_base_uom",
        "is_purchase_uom",
        "is_sales_uom",
        "is_stock_uom",
        "barcode",
        "is_active",
    ]
    success_url = reverse_lazy("master:item-uom-list")


class ItemUOMUpdateView(LoginRequiredMixin, UpdateView):
    model = ItemUOM
    template_name = "master/item_uom_form.html"
    fields = [
        "item",
        "uom",
        "conversion_factor",
        "is_base_uom",
        "is_purchase_uom",
        "is_sales_uom",
        "is_stock_uom",
        "barcode",
        "is_active",
    ]
    success_url = reverse_lazy("master:item-uom-list")


class ItemUOMDeleteView(LoginRequiredMixin, DeleteView):
    model = ItemUOM
    template_name = "master/item_uom_confirm_delete.html"
    success_url = reverse_lazy("master:item-uom-list")
