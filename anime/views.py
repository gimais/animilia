from django.shortcuts import render
from django.shortcuts import get_object_or_404

# Create your views here.
from anime.models import Anime


def pageView(request,slug):
    anime = get_object_or_404(Anime,slug=slug)
    return render(request,'anime/page.html',{'anime':anime})