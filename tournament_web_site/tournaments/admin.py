from django.contrib import admin
from .models import Team, Tournament, TeamRegistration, TournamentRegistration


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
	list_display = ['name', 'logo', 'commander', 'tournament']

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
	list_display = ['game', 'registration_start_date', 'start_date', 'team_size', 'maximum_number_of_teams', 'price']

@admin.register(TeamRegistration)
class TeamRegistrationAdmin(admin.ModelAdmin):
	list_display = ['team', 'player', 'date']

@admin.register(TournamentRegistration)
class TournamentRegistrationAdmin(admin.ModelAdmin):
	list_display = ['tournament', 'team', 'date', 'created_by', 'status']
