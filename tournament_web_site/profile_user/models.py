from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватарка', blank=True, null=True) # Поле для загрузки изображения, путь к картинкам - avatars/
    team = models.ForeignKey('tournaments.Team', blank=True, null=True, on_delete=models.SET_NULL)
    email = models.EmailField(verbose_name='email address', unique=True)

    def __str__(self):
        return f'{self.username}'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
