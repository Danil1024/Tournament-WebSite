from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(verbose_name='Возраст', blank=True, null=True) # Возраст, может быть пустым
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватарка', blank=True, null=True) # Поле для загрузки изображения, путь к картинкам - avatars/

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] # Обязательные поля при создании пользователя, кроме логина и пароля

    def __str__(self):
        return self.username
