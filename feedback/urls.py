from django.urls import path

from feedback.views import feedback

urlpatterns = [
    path('', feedback, name='feedback'),
]
