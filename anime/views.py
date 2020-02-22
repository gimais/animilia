from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import models
from anime.models import Anime, AnimeSeries

# Create your views here.


def pageView(request,slug):
    anime = get_object_or_404(Anime,slug=slug)
    genres = anime.categories.all()
    last_uploaded = AnimeSeries.objects.filter(anime=anime).aggregate(largest=models.Max('row'))['largest']
    return render(request,'anime/page.html',{'anime':anime,'genres':genres,'last_uploaded':last_uploaded})