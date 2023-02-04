from django.urls import path

from . import views

app_name = 'errands'
urlpatterns = [
    path('', views.UserErrandsList.as_view(), name='index'),
    path('<int:pk>/', views.DetailErrandView.as_view(), name='detail'),
    path('<int:pk>/update/', views.update, name='update'),
    path('new/', views.CreateErrandView.as_view(), name='new'),
    path('create/', views.create, name='create'),
    path('<int:pk>/export_history_csv/', views.csv_history, name='export_history_csv')
]
