
from django.urls import path

from . import views
app_name = 'thread'

urlpatterns = [
    # path('<int:pk>/', views.TopicDetailView.as_view(), name='topic'),
    path('create_topic/', views.TopicCreateView.as_view(), name='create_topic'),
    path('<int:pk>/', views.TopicAndCommentView.as_view(), name='topic'),
    path('category/<str:url_code>/', views.CategoryView.as_view(), name='category'),
]
