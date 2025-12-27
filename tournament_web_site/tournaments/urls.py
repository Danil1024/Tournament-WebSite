from django.urls import path
from .views import (
    MainPage, TournamentsPage, TournamentPage, MyTeams, TeamPage, 
    CreateTeamView, JoinTeamView, SettingTeamView, EditTeamView, 
    InvitePlayerView, KickPlayerView, AcceptApplicationView, RejectApplicationView
)

urlpatterns = [
    path("", MainPage.as_view(), name="main_page"),
    path("tournaments/", TournamentsPage.as_view(), name="tournaments"),
    path('tournament/<int:pk>/', TournamentPage.as_view(), name='tournament'),
    path("my-teams/", MyTeams.as_view(), name="my-teams"),
    path("team/<slug:slug>/", TeamPage.as_view(), name="team"),
    path("create-team/", CreateTeamView.as_view(), name="create-team"),
    path("join-team/", JoinTeamView.as_view(), name="join-team"),
    path("team/<slug:slug>/manage/", SettingTeamView.as_view(), name="team-setting"),
    
    # API endpoints для управления командой
    path("team/<slug:slug>/edit/", EditTeamView.as_view(), name="edit-team"),
    path("team/<slug:slug>/invite/", InvitePlayerView.as_view(), name="invite-player"),
    path("team/<slug:slug>/kick/", KickPlayerView.as_view(), name="kick-player"),
    path("team/<slug:slug>/accept-application/", AcceptApplicationView.as_view(), name="accept-application"),
    path("team/<slug:slug>/reject-application/", RejectApplicationView.as_view(), name="reject-application"),
]