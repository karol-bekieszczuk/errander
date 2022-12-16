from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('login_user/', views.login_user, name="login"),
    path('profile/', views.profile, name="profile"),
]
