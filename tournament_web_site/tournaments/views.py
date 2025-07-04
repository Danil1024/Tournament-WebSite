from django.views.generic import ListView, DetailView
from .models import Tournament, TournamentRegistration
from games.models import Game
from datetime import datetime

class MainPage(ListView):
    model = Tournament
    template_name = "tournaments/main_page.html"
    context_object_name = "tournaments"
    ordering = ['start_date']

class TournamentsPage(ListView):
    model = Tournament
    template_name = "tournaments/tournaments.html"
    context_object_name = "tournaments"
    ordering = ['start_date']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET

        date = params.get('date')
        game = params.get('game')
        team = params.get('team')

        if date:
            qs = qs.filter(start_date__date=date)
        
        if game:
            qs = qs.filter(game__name__iexact=game)
        
        if team:
            team_size_map = Tournament.get_team_size_mapper()
            qs = qs.filter(team_size__iexact=team_size_map.get(team))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unique_dates = []
        for tournament in Tournament.objects.get_queryset().order_by('-start_date'):
            start_date = tournament.start_date

            if start_date.replace(tzinfo=None) <= datetime.today().replace(tzinfo=None):
                continue

            start_date = start_date.date()
            if start_date not in unique_dates:
                unique_dates.append(start_date)
        
        games = Game.objects.get_queryset()

        context['games'] = games
        context['unique_dates'] = unique_dates[-1::-1]
        return context

class TournamentPage(DetailView):
    model = Tournament
    template_name = "tournaments/tournament.html"  # путь к шаблону
    context_object_name = "tournament"  # имя переменной в шаблоне

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament = self.object
        Tournament_registrations = TournamentRegistration.objects.filter(tournament=tournament)

        prize_fund = int(tournament.price) * len(Tournament_registrations)
        remaining_places = int(tournament.maximum_number_of_teams) - len(Tournament_registrations)

        context['prize_fund'] = prize_fund
        context['remaining_places'] = remaining_places

        return context
