from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django import forms
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import Tournament, TournamentRegistration, Team, TeamRegistration, TeamComposition
from .services.registration import TournamentRegistrationService
from .forms import JoinTeamForm
from games.models import Game
from django.db.models import Q
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime
import re


class CommanderPermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        # Получаем команду из slug параметра
        slug = kwargs.get('slug')
        if slug:
            team = get_object_or_404(Team, slug=slug)
            if request.user != team.commander:
                messages.error(request, 'У вас нет прав для управления этой командой')
                return redirect('team', slug=team.slug)
        return super().dispatch(request, *args, **kwargs)


class MainPage(ListView):
    model = Tournament
    template_name = "tournaments/main_page.html"
    context_object_name = "tournaments"
    ordering = ['start_date']

class TournamentsPage(ListView):
    model = Tournament
    template_name = "tournaments/tournaments.html"
    context_object_name = "tournaments"
    ordering = ['start_date']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET

        date = params.get('date')
        game = params.get('game')
        team = params.get('team')

        if date:
            qs = qs.filter(start_date__date=date)
        
        if game:
            qs = qs.filter(game__name__iexact=game)
        
        if team:
            team_size_map = Tournament.get_team_size_mapper()
            qs = qs.filter(team_size__iexact=team_size_map.get(team))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unique_dates = []
        for tournament in Tournament.objects.get_queryset().order_by('-start_date'):
            start_date = tournament.start_date

            if start_date.replace(tzinfo=None) <= datetime.today().replace(tzinfo=None):
                continue

            start_date = start_date.date()
            if start_date not in unique_dates:
                unique_dates.append(start_date)
        
        games = Game.objects.get_queryset()

        context['games'] = games
        context['unique_dates'] = unique_dates[-1::-1]
        return context

class TournamentPage(DetailView):
    model = Tournament
    template_name = "tournaments/tournament.html"
    context_object_name = "tournament"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament = self.object
        Tournament_registrations = TournamentRegistration.objects.filter(tournament=tournament)

        prize_fund = int(tournament.price) * len(Tournament_registrations)
        remaining_places = int(tournament.maximum_number_of_teams) - len(Tournament_registrations)

        if self.request.user.is_authenticated:
            user = self.request.user
            comands = Team.objects.filter(commander=user).prefetch_related('players')
        else:
            comands = Team.objects.none()

        teams_data = {}
        commanders_data = {}

        for team in comands:
            team_id = str(team.id)
            players = []
            for player in team.players.all():
                players.append({'id': player.id, 'username': player.username})
            teams_data[team_id] = players
            commanders_data[team_id] = team.commander_id

        teams_config = {
            'max_roster_size': int(tournament.team_size),
            'teams': teams_data,
            'commanders': commanders_data,
        }

        context['prize_fund'] = prize_fund
        context['remaining_places'] = remaining_places
        context['my_teams'] = comands
        context['teams_config'] = teams_config

        return context


class RegisterForTournamentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        data = request.data
        team_id = data.get('team_id')
        roster = data.get('roster')
        
        team = get_object_or_404(Team, pk=team_id)
        players = get_user_model().objects.filter(id__in=roster)

        registration_service = TournamentRegistrationService(
            tournament=tournament,
            team=team,
            players=players,
            user=request.user
        )
        try:
            registration_service.register()
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Заявка на турнир успешно подана'}, status=status.HTTP_201_CREATED)


class MyTeams(ListView):
    model = Team
    template_name = "tournaments/my_teams.html"
    context_object_name = "my_teams"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return Team.objects.filter(Q(commander=user) | Q(players=user)).distinct()
        else:
            return Team.objects.none()

class TeamPage(DetailView):
    model = Team
    template_name = "tournaments/team.html"
    context_object_name = "team"

class CreateTeamView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = "tournaments/create_team.html"
    fields = ['name', 'logo']
    success_url = reverse_lazy('my-teams')

    def form_valid(self, form):
        form.instance.commander = self.request.user
        response = super().form_valid(form)
        # Добавляем создателя команды как игрока
        form.instance.players.add(self.request.user)
        return response

class JoinTeamView(LoginRequiredMixin, CreateView):
    model = TeamRegistration
    form_class = JoinTeamForm
    template_name = "tournaments/join_team.html"
    success_url = reverse_lazy('my-teams')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.player = self.request.user
        form.instance.team = form.cleaned_data['team']
        form.instance.status = 'pending'

        return super().form_valid(form)

class SettingTeamView(CommanderPermissionMixin, LoginRequiredMixin, DetailView):
    model = Team
    template_name = "tournaments/team_setting.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team_registration'] = TeamRegistration.objects.filter(team=self.object, status='pending')
        return context

class EditTeamView(CommanderPermissionMixin, LoginRequiredMixin, View):
    def post(self, request, slug):
        team = get_object_or_404(Team, slug=slug)
        
        name = request.POST.get('name')
        logo = request.FILES.get('logo')
        
        if name and name != team.name:
            # Проверяем, что название соответствует требованиям
            if not re.match(r'^[a-z]+(?: [a-z]+)*$', name):
                messages.error(request, 'Название команды может содержать только маленькие латинские буквы и пробелы между словами')
                return redirect('team-setting', slug=team.slug)
            
            # Проверяем уникальность названия
            if Team.objects.filter(name=name).exclude(pk=team.pk).exists():
                messages.error(request, 'Команда с таким названием уже существует')
                return redirect('team-setting', slug=team.slug)
            
            team.name = name
        
        if logo:
            team.logo = logo
        
        team.save()
        messages.success(request, 'Команда успешно обновлена')
        return redirect('team-setting', slug=team.slug)

class InvitePlayerView(CommanderPermissionMixin, LoginRequiredMixin, View):
    def post(self, request, slug):
        team = get_object_or_404(Team, slug=slug)
        
        username = request.POST.get('player_username')
        if not username:
            messages.error(request, 'Введите никнейм игрока')
            return redirect('team-setting', slug=team.slug)
        
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            messages.error(request, f'Пользователь с никнеймом "{username}" не найден')
            return redirect('team-setting', slug=team.slug)
        
        # Проверяем, не состоит ли игрок уже в команде
        if user in team.players.all():
            messages.error(request, f'Игрок {username} уже состоит в команде')
            return redirect('team-setting', slug=team.slug)
        
        # Проверяем, нет ли уже заявки от этого игрока
        if TeamRegistration.objects.filter(team=team, player=user).exists():
            messages.error(request, f'Игрок {username} уже подал заявку в команду')
            return redirect('team-setting', slug=team.slug)
        
        # Создаем заявку
        TeamRegistration.objects.create(
            team=team,
            player=user,
            status='pending'
        )
        
        messages.success(request, f'Приглашение отправлено игроку {username}')
        return redirect('team-setting', slug=team.slug)

class KickPlayerView(CommanderPermissionMixin, LoginRequiredMixin, View):
    def post(self, request, slug):
        team = get_object_or_404(Team, slug=slug)
        
        player_id = request.POST.get('player_id')
        if not player_id:
            messages.error(request, 'Не указан игрок для исключения')
            return redirect('team-setting', slug=team.slug)
        
        try:
            player = get_user_model().objects.get(id=player_id)
        except get_user_model().DoesNotExist:
            messages.error(request, 'Игрок не найден')
            return redirect('team-setting', slug=team.slug)
        
        # Проверяем, что игрок действительно состоит в команде
        if player not in team.players.all():
            messages.error(request, 'Игрок не состоит в команде')
            return redirect('team-setting', slug=team.slug)
        
        # Нельзя исключить командира
        if player == team.commander:
            messages.error(request, 'Нельзя исключить командира команды')
            return redirect('team-setting', slug=team.slug)
        
        # Удаляем игрока из команды
        team.players.remove(player)
        
        # Удаляем все заявки этого игрока в эту команду
        TeamRegistration.objects.filter(team=team, player=player).delete()
        
        messages.success(request, f'Игрок {player.username} исключен из команды')
        return redirect('team-setting', slug=team.slug)

class AcceptApplicationView(CommanderPermissionMixin, LoginRequiredMixin, View):
    def post(self, request, slug):
        team = get_object_or_404(Team, slug=slug)
        
        application_id = request.POST.get('application_id')
        if not application_id:
            messages.error(request, 'Не указана заявка для принятия')
            return redirect('team-setting', slug=team.slug)
        
        try:
            application = TeamRegistration.objects.get(
                id=application_id,
                team=team,
                status='pending'
            )
        except TeamRegistration.DoesNotExist:
            messages.error(request, 'Заявка не найдена')
            return redirect('team-setting', slug=team.slug)
        
        # Добавляем игрока в команду
        team.players.add(application.player)
        
        # Удаляем заявку
        application.delete()
        
        messages.success(request, f'Игрок {application.player.username} принят в команду')
        return redirect('team-setting', slug=team.slug)

class RejectApplicationView(CommanderPermissionMixin, LoginRequiredMixin, View):
    def post(self, request, slug):
        team = get_object_or_404(Team, slug=slug)
        
        application_id = request.POST.get('application_id')
        if not application_id:
            messages.error(request, 'Не указана заявка для отклонения')
            return redirect('team-setting', slug=team.slug)
        
        try:
            application = TeamRegistration.objects.get(
                id=application_id,
                team=team,
                status='pending'
            )
        except TeamRegistration.DoesNotExist:
            messages.error(request, 'Заявка не найдена')
            return redirect('team-setting', slug=team.slug)
        
        # Удаляем заявку
        application.delete()
        
        messages.success(request, f'Заявка от {application.player.username} отклонена')
        return redirect('team-setting', slug=team.slug)