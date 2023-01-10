from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'errands'
urlpatterns = [
    path('', login_required(views.UserErrandsList.as_view()), name='user_errands'),
    path('<int:pk>/', login_required(views.DetailView.as_view()), name='detail'),
    path('<int:errand_id>/update/', login_required(views.update), name='update')
]
