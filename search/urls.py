from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.SerachResultView.as_view(), name='result'),
]
