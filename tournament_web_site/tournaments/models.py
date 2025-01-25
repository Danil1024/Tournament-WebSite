from django.db import models
from profile_user.models import CustomUser
from games.models import Game


class Tournament(models.Model):
    game = models.ForeignKey(Game, verbose_name='Игра', on_delete=models.CASCADE)
    registration_start_date = models.DateTimeField(verbose_name='Дата начала регистрации')
    start_date = models.DateTimeField(verbose_name='Дата начала турнира')
    team_size = models.CharField(verbose_name='Размер команды', max_length=1, choices=(('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')))
    maximum_number_of_teams = models.IntegerField(verbose_name='Максимальное количество команд')
    
    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турниры'

class Team(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)
    logo = models.ImageField(upload_to='logo/', verbose_name='Логотип', blank=True, null=True)
    commander = models.OneToOneField(CustomUser, verbose_name='Командир', on_delete=models.CASCADE, related_name='commander')
    tournament = models.ForeignKey(Tournament, verbose_name='Турнир', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

class TeamRegistration(models.Model):
    team = models.ForeignKey(Team, verbose_name='Команда', on_delete=models.CASCADE)
    player = models.OneToOneField(CustomUser, verbose_name='Игрок', on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name='Дата подачи заявки')
    
    class Meta:
        verbose_name = 'Заявка в команду'
        verbose_name_plural = 'Заявки в команды'

class TournamentRegistration(models.Model):
    tournament = models.ForeignKey(Tournament, verbose_name='Турнир', on_delete=models.CASCADE)
    team = models.OneToOneField(Team, verbose_name='Команда', on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name='Дата подачи заявки')
    
    class Meta:
        verbose_name = 'Заявка на турнир'
        verbose_name_plural = 'Заявки на турниры'
