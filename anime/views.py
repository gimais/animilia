from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from anime.models import Anime
from account.forms import CommentForm


ERROR = {'error':'მოხდა შეცდომა!'}

def page_view(request,slug):
    template_name = 'anime/page.html'
    anime = get_object_or_404(Anime.objects.prefetch_related('series','categories'),slug=slug)
    comments = anime.comments.with_annotates(request.user.pk).\
        prefetch_related('like','dislike','replies').\
        filter(active=True,parent__isnull=True)
    paginator = Paginator(comments,6)
    comments = paginator.get_page(1)
    comment_form = CommentForm
    return render(request,template_name,{'anime':anime,
                                         'comments':comments,
                                         'max_page':paginator.num_pages,
                                         'comment_form': comment_form,
                                         })

def more_comments(request):
    try:
        page = int(request.GET.get('skip',False))
        anime = Anime.objects.get(id=request.GET.get('id',None))
    except (Anime.DoesNotExist,Anime.MultipleObjectsReturned):
        anime = None
        page = None

    if anime and page:
        comments = anime.comments.filter(active=True,parent__isnull=True)
        paginator = Paginator(comments,6)
        if paginator.num_pages >= page:
            result = list()
            for comment in paginator.get_page(page).object_list:
                result.append(comment.get_more_comment_info())
            return JsonResponse(result, status=200, safe=False)
        else:
            return JsonResponse(ERROR, status=404)
    else:
        return JsonResponse(ERROR, status=400)