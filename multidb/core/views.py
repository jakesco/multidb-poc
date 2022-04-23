from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from .models import Item


class Index(LoginRequiredMixin, ListView):
    model = Item
    template_name = "core/index.html"
    context_object_name = "item_list"

    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        username = self.request.user.username
        return Item.objects.using(username).all()

    def post(self, request, *args, **kwargs):
        data = request.POST
        username = self.request.user.username
        Item.objects.using(username).create(name=data["item"], user=request.user.username)
        return HttpResponseRedirect('/')
