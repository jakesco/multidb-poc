from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Item


class Index(LoginRequiredMixin, ListView):
    model = Item
    template_name = "core/index.html"
    context_object_name = "item_list"

    login_url = '/login'
    redirect_field_name = 'redirect_to'
