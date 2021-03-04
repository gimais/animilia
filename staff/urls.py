from django.urls import path

from . import views
from .admin import staff_site

urlpatterns = [
    path('', staff_site.urls),
    path('avatar_delete/<int:id>', views.avatar_delete, name='delete_avatar'),
    path('show_info/<int:id>', views.show_info, name='show_info'),
    path('send_message/<int:user>', views.send_message, name='send_message'),
]
