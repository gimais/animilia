from django.urls import path
from .views import *

urlpatterns = [
    path('', index_view, name='home'),
    path('anime/search', search_anime, name='search_anime'),
    path('anime/<slug:slug>', anime_page_view, name='page'),
    path('schedule/', schedule, name='schedule'),
]
