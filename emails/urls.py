from django.urls import path

from . import views

app_name = 'emails'
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]
