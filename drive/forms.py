from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())

class SignupForm(UserCreationForm):
    # Add custom validators here if needed
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
