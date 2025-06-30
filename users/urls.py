from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import(login_view, signup_view, login)

app_name = "users"

urlpatterns = [
    path('login/', login, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', LogoutView.as_view(), name='logout')
]
