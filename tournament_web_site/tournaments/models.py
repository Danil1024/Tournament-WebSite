from django.db import models
from games.models import Game
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.db.models import F, Q
from django.db.models.constraints import CheckConstraint


class Tournament(models.Model):
    CHOICES_TEAM_SIZE = (
        ('1', 'solo'),
        ('2', 'duo'),
        ('3', 'trio'),
        ('4', 'squad'),
        ('5', 'full')
    )
    
    game = models.ForeignKey(Game, verbose_name='Игра', on_delete=models.CASCADE)
    creation_date = models.DateTimeField(verbose_name='Дата создания турнира', auto_now_add=True)
    registration_start_date = models.DateTimeField(verbose_name='Дата начала регистрации')
    start_date = models.DateTimeField(verbose_name='Дата начала турнира')
    team_size = models.CharField(verbose_name='Размер команды', max_length=1, choices=CHOICES_TEAM_SIZE)
    maximum_number_of_teams = models.PositiveIntegerField(verbose_name='Максимальное количество команд')
    price = models.PositiveIntegerField(verbose_name='Цена взноса')

    def __str__(self):
        return f'{self.game} {self.get_team_size_display()} #{self.pk}'
    
    @classmethod
    def get_team_size_map(cls):
        return {label: value for value, label in cls.CHOICES_TEAM_SIZE}
    
    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турниры'

        constraints = [
            CheckConstraint(
                check=Q(start_date__gte=F('registration_start_date')),
                name='start_date_after_or_equal_to_registration_start_date'
            ),
            CheckConstraint(
                check=Q(start_date__gte=F('registration_start_date') + timedelta(days=1)),
                name='min_1_day_between_registration_and_start'
            )
        ]

class Team(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)
    logo = models.ImageField(upload_to='logo/', verbose_name='Логотип', blank=True, null=True)
    commander = models.OneToOneField(get_user_model(), verbose_name='Командир', on_delete=models.CASCADE, related_name='commander')
    tournament = models.ForeignKey(Tournament, verbose_name='Турнир', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

class TeamRegistration(models.Model):
    team = models.ForeignKey(Team, verbose_name='Команда', on_delete=models.CASCADE)
    player = models.OneToOneField(get_user_model(), verbose_name='Игрок', on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name='Дата подачи заявки', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Заявка в команду'
        verbose_name_plural = 'Заявки в команды'

class TournamentRegistration(models.Model):
    CHOICES_STATUS = (('pending', 'ожидание'), ('pending payment', 'ожидание оплаты'), ('payment confirmed', 'подтверждения оплаты'), ('payment confirmed', 'оплата подтверждена'))
    tournament = models.ForeignKey(Tournament, verbose_name='Турнир', on_delete=models.CASCADE)
    team = models.OneToOneField(Team, verbose_name='Команда', on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name='Дата подачи заявки', auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), verbose_name='Модератор', on_delete=models.CASCADE)
    status = models.CharField(verbose_name='Статус', max_length=20, choices=CHOICES_STATUS)
    
    class Meta:
        verbose_name = 'Заявка на турнир'
        verbose_name_plural = 'Заявки на турниры'
