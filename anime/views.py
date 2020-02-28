from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from anime.models import Anime, AnimeSeries, Comment
from .forms import CommentForm
from .mixins import AjaxCommentFormMixin
from django.http import JsonResponse


def page_view(request,slug):
    template_name = 'anime/page.html'
    anime = get_object_or_404(Anime,slug=slug)
    episodes = AnimeSeries.objects.filter(anime=anime)
    comments = anime.comments.filter(active=True)
    comment_form = CommentForm
    return render(request,template_name,{'anime':anime,
                                         'episodes':episodes,
                                         'comments':comments,
                                         'comment_form': comment_form,
                                         })

# @login_required
class CommentFormView(AjaxCommentFormMixin, FormView):
    form_class = CommentForm
    success_url = '/success/'

def add_comment(request,slug):
    if request.is_ajax():
        form = CommentForm(request.POST)
        if form.is_valid():

            # comment = Comment(anime=Anime.objects.get(slug=slug),user=request.user,body=request.POST['body'])
            # comment.save()

            response_data = {
                'username':request.user.username,
                'avatar':'avataris surati',
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse(form.errors, status=400)
    else:
        return render(request,'anime/page.html')