from django.views.generic import ListView, DetailView
from .models import Tournament

class MainPage(ListView):
    model = Tournament
    template_name = "tournaments/main_page.html"
    context_object_name = "tournaments"
    ordering = ['-creation_date']
