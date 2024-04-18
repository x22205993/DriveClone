from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm, SignupForm

# Create your views here.
def login_view(request):
    ''' Login Form Handler '''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('drive:list')
            form.add_error(None, 'Invalid username or password')
        # Redirecting user to GET Login Page on error to prevent form resubmission on refresh . 
        # Since a fresh form will be rendered in the next request passing the current forms data and errors to session
        request.session['login_form_errors'] = form.errors
        return redirect('users:login')
    else:
        # Checking if the form being rendered had errors 
        form_errors = request.session.pop('login_form_errors', {})
        form = LoginForm()
        # Non Field Errors here would be when the user logs in with incorrect password or users.
        return render(request, 'login.html', {'form': form, 'form_errors': form_errors, 'non_field_errors': form_errors.get('__all__')})

def signup_view(request):
    ''' User Registration Handler '''
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
        # Redirecting user to GET Signup Page on error to prevent form resubmission on refresh . 
        # Since a fresh form will be rendered in the next request passing the current forms data and errors to session
        request.session['signup_form_data'] = form.data
        request.session['signup_form_errors'] = form.errors
        return redirect('users:signup')
    
    # Checking if the form being rendered had errors 
    form_data = request.session.pop('signup_form_data', None)
    form_errors = request.session.pop('signup_form_errors', None)
    form = SignupForm(data=form_data)
    return render(request, 'signup.html', {'form': form, 'form_errors': form_errors})