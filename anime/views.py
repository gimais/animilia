from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from anime.models import Anime, AnimeSeries, Comment
from .forms import CommentForm
from django.http import JsonResponse

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

@login_required
def add_comment(request,slug):
        if request.is_ajax():
            anime = Anime.objects.get(slug=slug) # anime object from current page
            form = CommentForm(request.POST)
            if form.is_valid():
                try:
                    parent_id = int(request.POST.get('parent_id'))
                except:
                    parent_id = None

                if parent_id:
                    reply_comment = form.save(commit=False)
                    reply_comment.anime = anime
                    reply_comment.parent = Comment.objects.get(id=parent_id)
                    reply_comment.user = request.user
                    reply_comment.save()
                else:
                    comment = form.save(commit=False)
                    comment.anime = anime
                    comment.user = request.user
                    comment.save()

                response_data = {
                    'username':request.user.username,
                    'avatar':'avataris surati',
                }
                return JsonResponse(response_data)
            else:
                return JsonResponse({'status':'400'}, status=400)
        else:
            return render(request,'anime/page.html')


def check_comments(request,int):
    if request.is_ajax():
        try:
            replies = Comment.objects.filter(parent=int,active=True)
        except:
            replies = None

        if replies:
            result = []
            for reply in replies:
                result.append(reply.get_reply_comment_info())
            return JsonResponse(result, status=200,safe=False)
        else:
            return JsonResponse({'error':'ar aqvs pasuxebi!!'},status=400)
    return JsonResponse({'error': 'moxda shecdoma!!'}, status=400)