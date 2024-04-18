from .views import login_view, logout_view, delete_story, StoryView
from django.urls import path

urlpatterns = [
    path('api/stories', StoryView.as_view(), name='stories'),
    path('api/stories/<int:key>', delete_story, name='delete_story'),
    path('api/login', login_view, name='login'),
    path('api/logout', logout_view, name='logout'),
]