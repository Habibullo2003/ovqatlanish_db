from django.views import generic
from django.urls import reverse_lazy
from .forms import RegisterForm
# Create your views here.

class RegisterView(generic.CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'