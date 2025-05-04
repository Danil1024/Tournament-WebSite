from django.db import models
from django.core.validators import FileExtensionValidator


class Game(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)
    icon = models.FileField(upload_to='./icons/', verbose_name='Иконка', validators=[FileExtensionValidator(['svg'])])

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'
