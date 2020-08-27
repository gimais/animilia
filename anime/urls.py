from django.urls import path
from . import views

urlpatterns = [
    path('', views.indexView, name='home'),
    path('anime/more_comments/', views.more_comments, name='more_comments'),
    path('anime/<slug:slug>/',views.page_view,name='page'),
]
