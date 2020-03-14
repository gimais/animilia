from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/',views.page_view,name='page'),
    path('more_comments', views.more_comments, name='more_comments'),
]
