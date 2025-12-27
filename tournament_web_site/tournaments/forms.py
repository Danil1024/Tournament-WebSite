from django import forms
from .models import Team, TeamRegistration


class JoinTeamForm(forms.ModelForm):
    
    team_name = forms.CharField(
        label='Название команды',
        max_length=20,
        widget=forms.TextInput(),
    )

    class Meta:
        model = TeamRegistration
        fields = ['team_name']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_team_name(self):
        team_name = self.cleaned_data['team_name']
        try:
            team = Team.objects.get(name=team_name)
            self.cleaned_data['team'] = team
            
            if hasattr(self, 'user') and self.user:
                existing_registration = TeamRegistration.objects.filter(
                    team=team,
                    player=self.user
                ).first()
                
                if existing_registration:
                    if existing_registration.status == 'pending':
                        raise forms.ValidationError('У вас уже есть активная заявка в эту команду')
                    elif existing_registration.status == 'accepted':
                        raise forms.ValidationError('Вы уже являетесь участником этой команды')
                    elif existing_registration.status == 'rejected':
                        raise forms.ValidationError('Ваша предыдущая заявка в эту команду была отклонена')
            
            return team_name
        except Team.DoesNotExist:
            raise forms.ValidationError('Команда с таким названием не найдена')
