from django.shortcuts import render
from django.shortcuts import get_object_or_404
from anime.models import Anime,Category
# Create your views here.

# MOVIE = 1
# SERIES = 2
#
# GENRES = {0:'კომედია',1:'საშინელება',2:'დრამა',3:'რომანტიკა',4:'დეტექტივი',5:'სათავგადასავლო'}
#
# db = [
#     {'name':'Naruto','an':51,'poster':1,'year':2004,'type':SERIES,'age':13,'genres':[GENRES[5],GENRES[2],GENRES[0]]},
#     {'name':'apukino','an':52,'poster':2,'year':2000,'type':MOVIE,'age':15,'genres':[GENRES[2]]},
#     {'name':'kapuchino','an':53,'poster':3,'year':2018,'type':SERIES,'age':25,'genres':[GENRES[4],GENRES[1]]},
#     {'name':'wgwg','an':53,'poster':3,'year':2018,'type':SERIES,'age':70,'genres':[GENRES[5],GENRES[1],GENRES[2],GENRES[3],GENRES[4],GENRES[0]]},
#     {'name':'apukino','an':52,'poster':2,'year':2000,'type':MOVIE,'age':15,'genres':[GENRES[2]]},
#     # {'name':'apukino','an':52,'poster':2,'year':2000,'type':MOVIE,'age':15,'genres':[GENRES[2]]},
#     # {'name':'apukino','an':52,'poster':2,'year':2000,'type':MOVIE,'age':15,'genres':[GENRES[2]]},
#     # {'name':'apukino','an':52,'poster':2,'year':2000,'type':MOVIE,'age':15,'genres':[GENRES[2]]},
#     #     {'name':'apukino','an':52,'poster':2,'year':2000,'type':MOVIE,'age':15,'genres':[GENRES[2]]},
#
# ]


def indexView(request):
    animes_list = Anime.objects.all()
    context = {anime:anime.categories.all() for anime in animes_list}
    return render(request,'home.html',{'animes_list':context})