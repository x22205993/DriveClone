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
        request.session['login_form_errors'] = form.errors
        return redirect('users:login')
    else:
        form_errors = request.session.pop('login_form_errors', {})
        form = LoginForm()
        return render(request, 'login.html', {'form': form, 'form_errors': form_errors, 'non_field_errors': form_errors.get('__all__')})

def signup_view(request):
    ''' User Registration Handler also creates a new bucket for every new user '''
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
        print(request.POST.dict)
        request.session['signup_form_data'] = form.data
        request.session['signup_form_errors'] = form.errors
        return redirect('users:signup')
    form_data = request.session.pop('signup_form_data', None)
    form_errors = request.session.pop('signup_form_errors', None)
    form = SignupForm(data=form_data)
    return render(request, 'signup.html', {'form': form, 'form_errors': form_errors})