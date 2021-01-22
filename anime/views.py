from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.db.models.expressions import RawSQL
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from account.forms import CommentForm
from account.models import Comment, Notification
from anime.models import Anime, Schedule

ERROR = {'error': 'moxda shecdoma!'}


def index_view(request):
    animes = Anime.objects.values('name', 'slug', 'age', 'rating', 'views', 'poster', 'soon').all().order_by(
        '-updated')

    paginator = Paginator(animes, 9)
    page = request.GET.get('page', 1)

    try:
        animes = paginator.get_page(page)
    except PageNotAnInteger:
        animes = paginator.page(1)
    except EmptyPage:
        animes = paginator.page(paginator.num_pages)

    return render(request, 'home.html', {'animes_list': animes})


def anime_page_view(request, slug):
    template_name = 'anime/page.html'
    anime = get_object_or_404(Anime.objects, slug__iexact=slug)
    anime.increase_view_count(request.COOKIES)
    context = {
        'anime': anime,
        'comment_form': CommentForm
    }

    if 'parent' in request.GET.keys():
        comments = anime.comments.related_objects_annotates(request.user).filter(
            Q(active=True) | Q(active_replies_count__gte=1),
            parent__isnull=True).order_by(
            RawSQL('CASE WHEN "account_comment"."id" = %s THEN 1 ELSE 2 END', (request.GET['parent'],)), 'priority',
            '-id')

        if 'notif' in request.GET.keys():
            try:
                notification = request.user.notification_set.get(id=int(request.GET['notif']), visited=False)
            except (Notification.DoesNotExist, ValueError):
                notification = None

            if notification is not None:
                notification.visited = True
                notification.save()
    else:
        comments = anime.comments.related_objects_annotates(request.user).filter(
            Q(active=True) | Q(active_replies_count__gte=1),
            parent__isnull=True)

    paginator = Paginator(comments, 6)
    comments = paginator.get_page(1)

    context['comments'] = comments
    context['max_page'] = paginator.num_pages
    return render(request, template_name, context)


def more_comments(request):
    try:
        anime_id = int(request.GET.get('id', False))
        page = int(request.GET.get('skip', False))
    except ValueError:
        anime_id = None
        page = None

    if page and anime_id:
        try:
            parent_id = int(request.GET.get('parent', False))
        except ValueError:
            parent_id = None

        if parent_id:
            comments = Comment.objects.related_objects_annotates(request.user).filter(
                Q(active=True) | Q(active_replies_count__gte=1), parent__isnull=True, anime=anime_id).order_by(
                RawSQL('CASE WHEN "account_comment"."id" = %s THEN 1 ELSE 2 END', (request.GET['parent'],)),
                'priority',
                '-id')
        else:
            comments = Comment.objects.related_objects_annotates(request.user).filter(
                Q(active=True) | Q(active_replies_count__gte=1),
                parent__isnull=True, anime_id=anime_id)

        paginator = Paginator(comments, 6)

        if paginator.num_pages >= page:
            result = list()
            for comment in paginator.get_page(page).object_list:
                if comment.active:
                    result.append(comment.get_more_comment_info(request.user.pk))
                else:
                    result.append(comment.get_deleted_comment_info())
            return JsonResponse(result, status=200, safe=False)
        else:
            return JsonResponse(ERROR, status=404)
    else:
        return JsonResponse(ERROR, status=400)


def schedule(request):
    objs = Schedule.objects.select_related('anime').values('date', 'from_time', 'text', 'to_time', 'anime__name',
                                                           'anime__poster', 'anime__slug',
                                                           max=Count('anime__series__row') + 1).all().order_by('date',
                                                                                                               'from_time')
    return render(request, 'schedule.html', {'schedule': objs})
