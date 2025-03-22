from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser

class RegisterForm(UserCreationForm):
    fullname = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ism va familiyangizni kiriting'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Emailni kiriting'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['fullname', 'username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parol'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parolni qayta kiriting'}),
        }
