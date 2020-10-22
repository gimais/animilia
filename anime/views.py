from django.core.paginator import Paginator
from django.db.models.expressions import RawSQL
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from account.models import Comment
from anime.models import Anime
from account.forms import CommentForm


ERROR = {'error':'moxda shecdoma!'}

def indexView(request):
    animes_list = Anime.objects.values('name','slug','age','rating','views','poster').all().order_by('-updated')
    return render(request,'home.html',{'animes_list':animes_list})

def page_view(request,slug):
    template_name = 'anime/page.html'
    anime = get_object_or_404(Anime.objects,slug__iexact=slug)
    anime.increase_view_count(request.COOKIES)
    context = {
        'anime':anime,
        'comment_form': CommentForm
    }

    if not len(request.GET):
        comments = anime.comments.with_annotates(request.user).filter(active=True, parent__isnull=True)
    else:
        comments = show_parent_comment_and_delete_notification(request,anime,context)

    paginator = Paginator(comments,6)
    comments = paginator.get_page(1)

    context['comments'] = comments
    context['max_page'] = paginator.num_pages

    return render(request,template_name,context)

def more_comments(request):
    try:
        anime_id = int(request.GET.get('id',False))
        page = int(request.GET.get('skip',False))
    except ValueError:
        anime_id = None
        page = None

    if page and anime_id:
        try:
            parent_id = int(request.GET.get('parent', False))
        except:
            parent_id = None

        if parent_id:
            comments = Comment.objects.with_annotates(request.user). \
            filter(active=True, parent__isnull=True). \
            annotate(target_item=RawSQL('"account_comment"."id" = %s', (parent_id,))).\
            order_by('-target_item','-id')
        else:
            comments = Comment.objects.filter(anime_id=anime_id, active=True, parent__isnull=True)

        paginator = Paginator(comments, 6)

        if paginator.num_pages >= page:
            result = list()
            for comment in paginator.get_page(page).object_list:
                result.append(comment.get_more_comment_info(request.user.pk))
            return JsonResponse(result, status=200, safe=False)
        else:
            return JsonResponse(ERROR, status=404)
    else:
        return JsonResponse(ERROR, status=400)


def show_parent_comment_and_delete_notification(request,anime,context):
    try:
        parent_comment = int(request.GET.get('parent', False))
    except ValueError:
        parent_comment = None

    if parent_comment:  # return parent_comment as first row, delete notification
        comments = anime.comments.with_annotates(request.user). \
            filter(active=True, parent__isnull=True). \
            annotate(target_item=RawSQL('"account_comment"."id" = %s', (parent_comment,))).\
            order_by('-target_item','-id')

        try:
            notif_id = int(request.GET.get('notif', False))
        except ValueError:
            notif_id = None

        if notif_id:
            from account.models import Notification
            try:
                notif_obj = Notification.objects.get(id=notif_id)
            except Notification.DoesNotExist:
                notif_obj = None

            if notif_obj is not None and notif_obj.user_id == request.user.id:
                notif_obj.delete()

                if str(comments.first()) != str(parent_comment):  # if comment is deleted
                    try:
                        deleted_parent_comment = Comment.objects.get(id=parent_comment).\
                            get_deleted_comment_for_notification_redirect()
                    except Comment.DoesNotExist:
                        deleted_parent_comment = None

                    if deleted_parent_comment:
                        context['deletedcomment'] = deleted_parent_comment

    else:
        comments = anime.comments.with_annotates(request.user).filter(active=True, parent__isnull=True)

    return comments