from django.urls import path
from .views import MainPage, TournamentsPage

urlpatterns = [
    path("", MainPage.as_view(), name="main_page"),
    path("tournaments/", TournamentsPage.as_view(), name="tournaments"),
]