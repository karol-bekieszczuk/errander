from django.urls import path

from . import views

app_name = 'errands'
urlpatterns = [
    path('', views.UserErrandsList.as_view(), name='user_errands'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:errand_id>/update/', views.update, name='update')
]
