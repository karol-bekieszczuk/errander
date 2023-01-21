from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login_user/', views.login_user, name="login_user"),
    path('logout_user/', views.logout_user, name="logout_user"),
    path('', views.profile, name="profile"),
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]
