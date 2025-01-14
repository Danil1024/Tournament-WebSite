from django.db import models


class Game(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)
    icon = models.ImageField(upload_to='icons/', verbose_name='Иконка', blank=True, null=True)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'
