from anime.models import Anime


def process_single_search_query(query: dict):
    field = next(iter(query.keys()), None)
    result = dict()

    if field is not None:
        result['animes'] = Anime.objects.distinct().filter(**{"{field}__name".format(field=field): query.get(field)}) \
            .values('name', 'slug', 'age', 'rating', 'views', 'poster', 'soon').order_by('-updated')
        result['filter_info'] = getattr(Anime, field).field.related_model.objects.filter(name=query.get(field)).first()
        result['template'] = 'anime/{name}.html'.format(name=field)

    return result
