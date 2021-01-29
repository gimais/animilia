from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='home'),
    path('anime/more_comments/', views.more_comments, name='more_comments'), # TODO ratoa es aq?
    path('anime/<slug:slug>', views.anime_page_view, name='page'),
    path('schedule/', views.schedule, name='schedule'),
]
