from django.contrib import admin
from .models import Team, Tournament, TeamRegistration, TournamentRegistration, TeamComposition, TeamResult


class PlayersListMixin:
	def get_queryset(self, request):
		qs = super().get_queryset(request)
		return qs.prefetch_related('players')
	
	def players_list(self, obj):
		names = [user.username for user in obj.players.all()]
		return ", ".join(names) if names else "-"
	players_list.short_description = 'Игроки'

@admin.register(Team)
class TeamAdmin(PlayersListMixin, admin.ModelAdmin):
	list_display = ['name', 'logo', 'commander', 'players_list']
	
@admin.register(TeamComposition)
class TeamCompositionAdmin(PlayersListMixin, admin.ModelAdmin):
	list_display = ['team', 'players_list', 'tournament']

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
	list_display = ['game', 'registration_start_date', 'start_date', 'team_size', 'maximum_number_of_teams', 'price']

	def get_readonly_fields(self, request, obj=None): 
		if obj:
			return ['start_date', 'registration_start_date', 'registration_end_date']
		return []

@admin.register(TeamRegistration)
class TeamRegistrationAdmin(admin.ModelAdmin):
	list_display = ['team', 'player', 'status']

@admin.register(TournamentRegistration)
class TournamentRegistrationAdmin(admin.ModelAdmin):
	list_display = ['tournament', 'team_composition', 'date', 'status']

@admin.register(TeamResult)
class TeamResultAdmin(admin.ModelAdmin):
	list_display = ['tournament', 'team', 'points']
