"""animilia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

AdminAuthenticationForm.error_messages = {
    'invalid_login':
        "გთხოვთ, შეიყვანოთ სწორი მომხმარებლის სახელი და პაროლი. "
        "იქონიეთ მხედველობაში, რომ ორივე ველი ითვალისწინებს პატარა და დიდ ასოებს."
        "ან ადმინი არ ხარ!!"
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('home.urls')),
    path('account/',include('account.urls')),
    path('anime/',include('anime.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
