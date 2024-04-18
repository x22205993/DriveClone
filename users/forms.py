from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core import validators
from django.core.validators import RegexValidator, MaxLengthValidator, validate_email
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user

name_validators = [RegexValidator(r'^[a-zA-Z ]*$', 'Invalid Input only letters are allowed'),
                   MaxLengthValidator(30, 'Username cannot be more than 30 characters')]
username_validators = [RegexValidator(r'^[a-zA-Z0-9_ ]*$', 'Invalid Input only letters, digits and _  are allowed'),
                       MaxLengthValidator(30, 'Username cannot be more than 30 characters')]


# pylint: disable=too-few-public-methods
class LoginForm(forms.Form):
    ''' Login Form fields and validations '''
    username = forms.CharField(validators=username_validators)
    password = forms.CharField(widget=forms.PasswordInput())

class SignupForm(UserCreationForm):
    ''' Signup form fields and validations '''
    email = forms.EmailField(validators=[validate_email])
    first_name = forms.CharField(validators=name_validators)
    last_name = forms.CharField(validators=name_validators)
    username = forms.CharField(validators=username_validators)

    class Meta:
        ''' Meta class for defining model '''
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
