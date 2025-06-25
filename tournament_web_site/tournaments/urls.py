from django.urls import path
from .views import MainPage, TournamentsPage, TournamentPage

urlpatterns = [
    path("", MainPage.as_view(), name="main_page"),
    path("tournaments/", TournamentsPage.as_view(), name="tournaments"),
    path('tournament/<int:pk>/', TournamentPage.as_view(), name='tournament'),
]