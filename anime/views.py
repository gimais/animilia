from django.shortcuts import render
from django.shortcuts import get_object_or_404
from anime.models import Anime, AnimeSeries
from account.forms import CommentForm

def page_view(request,slug):
    template_name = 'anime/page.html'
    anime = get_object_or_404(Anime,slug=slug)
    episodes = AnimeSeries.objects.filter(anime=anime)
    comments = anime.comments.filter(active=True,parent__isnull=True)
    comment_form = CommentForm
    return render(request,template_name,{'anime':anime,
                                         'episodes':episodes,
                                         'comments':comments,
                                         'comment_form': comment_form,
                                         })
