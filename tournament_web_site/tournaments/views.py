from django.views.generic import ListView, DetailView
from .models import Tournament

class MainPage(ListView):
    model = Tournament
    template_name = "tournaments/main_page.html"
    context_object_name = "tournaments"

    def get_queryset(self, *args, **kwargs):
        return Tournament.objects.order_by('-creation_date')[:4]
