from django.db import models
from games.models import Game
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
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

    STATUS_CHOICES = [
        ('completed', 'Завершен'),
        ('incomplete', 'Не завершен'),
    ]
    
    game = models.ForeignKey(Game, verbose_name='Игра', on_delete=models.CASCADE)

    creation_date = models.DateTimeField(verbose_name='Дата создания турнира', auto_now_add=True) 
    registration_start_date = models.DateTimeField(verbose_name='Дата начала регистрации', blank=True, null=True, help_text='Оставьте пустым, чтобы установить автоматически')
    registration_end_date = models.DateTimeField(verbose_name='Дата окончания регистрации', blank=True, null=True, help_text='Оставьте пустым, чтобы установить автоматически')
    start_date = models.DateTimeField(verbose_name='Дата начала турнира')

    team_size = models.CharField(verbose_name='Размер команды', max_length=1, choices=CHOICES_TEAM_SIZE)
    maximum_number_of_teams = models.PositiveIntegerField(verbose_name='Максимальное количество команд')
    price = models.PositiveIntegerField(verbose_name='Цена взноса')
    created_by = models.ForeignKey(get_user_model(), verbose_name='Модератор', on_delete=models.CASCADE)
    status = models.CharField(verbose_name='Статус', max_length=20, choices=STATUS_CHOICES)

    @classmethod
    def get_team_size_mapper(cls):
        return {label: value for value, label in cls.CHOICES_TEAM_SIZE}
    
    def __str__(self):
        return f'{self.game} {self.get_team_size_display()} #{self.pk}'
    
    def save(self, *args, **kwargs):
        if not self.pk: # первое сохранение (создание)
            # Инициируем дату начала регистрации равной дате создания
            self.registration_start_date = timezone.now()
            # Для конца регистрации всегда ставим старт турнира минус 1 час
            if self.start_date:
                self.registration_end_date = self.start_date - timedelta(hours=1)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турниры'

        constraints = [
            CheckConstraint(
                check=Q(start_date__gte=F('registration_start_date')),
                name='start_date_after_or_equal_to_registration_start_date'
            ),
        ]

class Team(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)
    logo = models.ImageField(upload_to='logo/', verbose_name='Логотип', blank=True, null=True)
    commander = models.ForeignKey(get_user_model(), verbose_name='Командир', on_delete=models.CASCADE, related_name='commander')
    players = models.ManyToManyField(get_user_model(), verbose_name='Игроки команды', related_name='team_players')

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

class TeamComposition(models.Model):
    team = models.ForeignKey(Team, verbose_name='Команда', on_delete=models.CASCADE)
    players = models.ManyToManyField(get_user_model(), verbose_name='Игроки состава', related_name='team_composition_players')
    tournament = models.ForeignKey(Tournament, verbose_name='Турнир', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Состав команды'
        verbose_name_plural = 'Составы команд'

class TeamResult(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='results', verbose_name='Турнир')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='results', verbose_name='Команда')
    points = models.PositiveIntegerField(verbose_name='Очки команды')

    class Meta:
        verbose_name = 'Результат команды'
        verbose_name_plural = 'Результаты команд'

class TeamRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]
    team = models.ForeignKey(Team, verbose_name='Команда', on_delete=models.CASCADE)
    player = models.ForeignKey(get_user_model(), verbose_name='Игрок', on_delete=models.CASCADE)
    status = models.CharField(verbose_name='Статус', max_length=20, choices=STATUS_CHOICES)
    
    class Meta:
        verbose_name = 'Заявка в команду'
        verbose_name_plural = 'Заявки в команды'

class TournamentRegistration(models.Model):
    STATUS_CHOICES = (
        ('pending payment', 'ожидание оплаты'),
        ('payment confirmed', 'оплата подтверждена'),
        ('payment_failed', 'оплата не прошла')
    )
    tournament = models.ForeignKey(Tournament, verbose_name='Турнир', on_delete=models.CASCADE)
    team_composition = models.OneToOneField(Team, verbose_name='Состав команды', on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name='Дата подачи заявки', auto_now_add=True)
    status = models.CharField(verbose_name='Статус', max_length=20, choices=STATUS_CHOICES)
    
    class Meta:
        verbose_name = 'Заявка на турнир'
        verbose_name_plural = 'Заявки на турниры'
