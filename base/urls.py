from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'base'

urlpatterns = [
    # path('', views.TopView.as_view(), name='top'),
    path('', views.TopicListView.as_view(), name='top'),
    path('terms/', TemplateView.as_view(template_name='base/terms.html'), name='terms'),
    path('policy/', TemplateView.as_view(template_name='base/policy.html'), name='policy'),
    path('about/', TemplateView.as_view(template_name='base/about.html'), name='about'),
]
