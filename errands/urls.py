from django.urls import path

from . import views

app_name = 'errands'
urlpatterns = [
    path('', views.UserErrandsList.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:errand_id>/update/', views.update, name='update'),
    path('new/', views.CreateErrandView.as_view(), name='new'),
    path('create/', views.create, name='create'),
]
