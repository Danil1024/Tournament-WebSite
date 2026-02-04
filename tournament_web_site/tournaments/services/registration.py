from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from ..models import TournamentRegistration, TeamComposition


class TournamentRegistrationService:
    def __init__(self, tournament, team, players, user):
        self.tournament = tournament
        self.team = team
        self.players = players
        self.user = user

    def validate(self):
        if self.team.commander != self.user:
            raise ValidationError('Вы не являетесь командиром этой команды')

        if self.players.count() != int(self.tournament.team_size):
            raise ValidationError('Неверное количество игроков в составе команды')

        if TournamentRegistration.objects.filter(
            tournament=self.tournament, team_composition__team=self.team
        ).exists():
            raise ValidationError('Ваша команда уже зарегистрирована на этот турнир')

        if TournamentRegistration.objects.filter(
            tournament=self.tournament, team_composition__players__in=self.players
        ).exists():
            raise ValidationError('Один или несколько игроков уже зарегистрированы на этот турнир')

        if TournamentRegistration.objects.filter(tournament=self.tournament).count() >= int(self.tournament.maximum_number_of_teams):
            raise ValidationError('Достигнуто максимальное количество команд для этого турнира')

        team_player_ids = list(self.team.players.values_list('id', flat=True))
        if not all(player.id in team_player_ids for player in self.players):
            raise ValidationError('Один или несколько игроков не состоят в вашей команде')


        if self.tournament.start_date <= now():
            raise ValidationError('Регистрация на этот турнир уже закрыта')

    def register(self):
        self.validate()
        with transaction.atomic():
            team_composition = TeamComposition.objects.create(team=self.team)
            team_composition.players.set(self.players)
            registration = TournamentRegistration.objects.create(
                tournament=self.tournament,
                team_composition=team_composition,
                status='pending payment'
            )
        return registration
