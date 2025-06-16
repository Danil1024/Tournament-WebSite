from django import forms
from django.forms import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Пароль',
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Подтвердите пароль',
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username']

        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким никнеймом уже существует.')
        if username.isdigit():
            raise ValidationError('Никнейм не может состоять только из цифр.')
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']

        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Эта почта уже зарегистрирована.')
        
        return email
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'avatar')
        
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Никнейм',
                'spellcheck': 'false',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Электронная почта',
            }),
        }

class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label='Запомнить меня')

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Никнейм',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Пароль',
        })
    )