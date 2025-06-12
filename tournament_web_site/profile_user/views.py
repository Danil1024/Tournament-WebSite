from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegistrationForm, LoginForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as DefaultLoginView


class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'profile_user/register.html'
    success_url = reverse_lazy('main_page')

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

class LoginView(DefaultLoginView):
    form_class = LoginForm
    template_name = 'profile_user/login.html'
