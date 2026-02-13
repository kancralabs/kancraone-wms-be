from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from .models import Company


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = "organizations/company_list.html"
    context_object_name = "companies"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(legal_name__icontains=search)
                | Q(city__icontains=search),
            )
        return queryset


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = "organizations/company_detail.html"
    context_object_name = "company"


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    template_name = "organizations/company_form.html"
    fields = [
        "code",
        "name",
        "legal_name",
        "company_type",
        "tax_id",
        "phone",
        "email",
        "website",
        "address",
        "city",
        "state",
        "postal_code",
        "country",
        "currency",
        "payment_terms",
        "credit_limit",
        "is_active",
        "notes",
    ]
    success_url = reverse_lazy("organizations:company-list")


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    template_name = "organizations/company_form.html"
    fields = [
        "code",
        "name",
        "legal_name",
        "company_type",
        "tax_id",
        "phone",
        "email",
        "website",
        "address",
        "city",
        "state",
        "postal_code",
        "country",
        "currency",
        "payment_terms",
        "credit_limit",
        "is_active",
        "notes",
    ]
    success_url = reverse_lazy("organizations:company-list")


class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = "organizations/company_confirm_delete.html"
    success_url = reverse_lazy("organizations:company-list")
