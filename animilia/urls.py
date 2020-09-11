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
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from account.views import profile_preview
from templates.sitemaps import AnimeSitemap
from django.contrib.sitemaps.views import sitemap
from feedback.views import feedback_form

sitemaps = {
    'animes':AnimeSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('feedback/', feedback_form,name='feedback'),
    path('account/',include('account.urls')),
    path('profile/<int:id>/',profile_preview,name='profile_preview'),
    path('sitemap.xml', sitemap, {'sitemaps':sitemaps},name='sitemap'),
    path('',include('anime.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)