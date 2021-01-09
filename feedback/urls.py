from django.urls import path
from .views import feedback, get_message


urlpatterns = [
    path('', feedback, name='feedback'),
    path('message/<int:id>', get_message, name='feedback'),
]
