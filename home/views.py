from django.shortcuts import render
from django.shortcuts import get_object_or_404
from anime.models import Anime, Category, AnimeSeries
from django.db import models


# Create your views here.


def count_episodes_by_anime(anime):
   return AnimeSeries.objects.filter(anime=anime).aggregate(largest=models.Max('row'))['largest']

def indexView(request):
    animes_list = Anime.objects.all().order_by('-updated')
    try:
        context = {anime:[anime.categories.all(),count_episodes_by_anime(anime)] for anime in animes_list}
    except:
        context = {}
    return render(request,'home.html',{'animes_list':context})