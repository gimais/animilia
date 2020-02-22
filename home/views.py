from django.shortcuts import render
from django.shortcuts import get_object_or_404
from anime.models import Anime,Category
# Create your views here.


def indexView(request):
    animes_list = Anime.objects.all()
    try:
        context = {anime:anime.categories.all() for anime in animes_list}
    except:
        context = {}
    return render(request,'home.html',{'animes_list':context})