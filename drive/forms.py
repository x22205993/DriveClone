from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user

# pylint: disable=too-few-public-methods

class LoginForm(forms.Form):
    ''' Login Form fields and validations '''
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())

class SignupForm(UserCreationForm):
    ''' Signup form fields and validations '''
    class Meta:
        ''' Meta class for defining model '''
        model = User
        fields = ['username', 'email', 'password1', 'password2']
