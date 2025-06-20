from django.contrib import admin
from .models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
	list_display = ['name', 'icon']
	prepopulated_fields = {"slug": ("name",)}
