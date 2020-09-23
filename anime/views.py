from django.core.paginator import Paginator
from django.db.models import CharField, IntegerField, Value
from django.db.models.expressions import RawSQL
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from anime.models import Anime
from account.forms import CommentForm


ERROR = {'error':'მოხდა შეცდომა!'}

def indexView(request):
    animes_list = Anime.objects.values('name','slug','age','rating','views','poster').all().order_by('-updated')
    return render(request,'home.html',{'animes_list':animes_list})

def page_view(request,slug):
    template_name = 'anime/page.html'
    anime = get_object_or_404(Anime.objects.prefetch_related('series','categories','comments','dubbers'),slug=slug)
    anime.increase_view_count(request.COOKIES)

    if not len(request.GET):
        comments = anime.comments.with_annotates(request.user).filter(active=True, parent__isnull=True)
    else:
        try:
            parent_comment = int(request.GET.get('parent', False))
            notif_id = int(request.GET.get('notif', False))
        except ValueError:
            parent_comment = None
            notif_id = None

        if parent_comment: #return parent_comment as first row, delete notification
            comments = anime.comments.with_annotates(request.user).\
                filter(active=True, parent__isnull=True).\
                annotate(target_item=RawSQL('"account_comment"."id" = %s', (parent_comment,))).order_by('-target_item','-id')

            if notif_id:
                from account.models import Notification as Notif
                try:
                    notif_obj = Notif.objects.get(id=notif_id)
                except Notif.DoesNotExist:
                    notif_obj = None

                if comments.first().id == parent_comment and notif_obj is not None and notif_obj.user_id == request.user.id:
                    notif_obj.delete()
        else:
            comments = anime.comments.with_annotates(request.user).filter(active=True, parent__isnull=True)

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
        anime = Anime.objects.prefetch_related('comments').get(id=request.GET.get('id',None))
    except (Anime.DoesNotExist,Anime.MultipleObjectsReturned):
        anime = None
        page = None

    if anime and page:
        comments = anime.comments.filter(active=True,parent__isnull=True)
        paginator = Paginator(comments,6)
        if paginator.num_pages >= page:
            result = list()
            for comment in paginator.get_page(page).object_list:
                result.append(comment.get_more_comment_info(request.user.pk))
            return JsonResponse(result, status=200, safe=False)
        else:
            return JsonResponse(ERROR, status=404)
    else:
        return JsonResponse(ERROR, status=400)