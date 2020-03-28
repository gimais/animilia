from django.shortcuts import render
from anime.models import Anime
from django.db import models

# Create your views here.

def indexView(request):
    animes_list = Anime.objects.values('name','slug','age','rating','views','poster').all().order_by('-updated')
    return render(request,'home.html',{'animes_list':animes_list})