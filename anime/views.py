from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.db.models.expressions import Case, When
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from account.forms import CommentForm
from anime.filter import process_single_search_query
from anime.models import Anime, Schedule, ChronologyItem


def paginate_page(content, page):
    paginator = Paginator(content, 9)

    try:
        content = paginator.get_page(page)
    except PageNotAnInteger:
        content = paginator.page(1)
    except EmptyPage:
        content = paginator.page(paginator.num_pages)

    return content


def index_view(request):
    animes = Anime.objects.values('name', 'slug', 'age', 'rating', 'views', 'poster', 'soon').order_by('-updated')

    return render(request, 'home.html', {'animes_list': paginate_page(animes, request.GET.get('page', 1))})


def anime_page_view(request, slug):
    anime = get_object_or_404(Anime.objects, slug__iexact=slug)
    anime.increase_view_count(request.COOKIES)
    context = {
        'anime': anime,
        'chronology': ChronologyItem.objects.select_related('anime').filter(
            chronology__in=ChronologyItem.objects.select_related('anime')
                .filter(anime=anime).values('chronology_id')).order_by('id')
            .values('anime__name', 'anime__slug', 'not_here', 'anime__type', 'anime__episodes'),
        'types': Anime.TYPES,
        'status': Anime.STATUS,
        'comment_form': CommentForm
    }

    parent = request.GET.get('parent', None)
    if parent and parent.isdecimal():

        comments = anime.comments.annotates_related_objects(request.user).filter(
            Q(active=True) | Q(active_children_count__gte=1),
            parent__isnull=True).order_by(
            Case(
                When(id=parent, then=1),
                default=2,
            ),
            '-priority',
            '-id')

        notification = request.GET.get('notif', None)

        if notification and notification.isdecimal():
            request.user.notifications.filter(id=notification, seen=False).update(seen=True)
    else:
        comments = anime.comments.annotates_related_objects(request.user).filter(
            Q(active=True) | Q(active_children_count__gte=1),
            parent__isnull=True)

    paginator = Paginator(comments, 6)
    comments = paginator.get_page(1)

    context['comments'] = comments
    context['max_page'] = paginator.num_pages
    return render(request, 'anime/page.html', context)


def schedule(request):
    schedule = Schedule.objects.select_related('anime'). \
        values('date', 'from_time', 'text', 'to_time', 'anime__name', 'anime__poster',
               'anime__slug', max=Count('anime__videos__row') + 1).all()
    return render(request, 'schedule.html', {'schedule': schedule})


def search_anime(request):
    params = {field: value for field, value in request.GET.items()
              if value and field in Anime.searchable_fields()}

    filter: dict = process_single_search_query(params)
    if filter.get('filter_info', None) is None:
        return index_view(request)

    query = QueryDict(request.GET.urlencode(), mutable=True)
    query.pop('page', None)

    return render(request, 'anime/filter.html', {
        'params': query.urlencode(),
        'template': filter.get('template'),
        'filter_info': filter.get('filter_info'),
        'animes_list': paginate_page(filter.get('animes'), request.GET.get('page', 1))
    })
