from django.urls import path, re_path
from . import views
from haystack.views import SearchView

app_name = 'main'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('play/<int:id>/', views.play, name='play'),
    path('detail/<int:id>/', views.detail, name='detail'),
    path(r'add_videos/', views.add_video_path, name='add'),
    path('search/', SearchView())
]
