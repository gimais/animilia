from django.contrib.sitemaps import Sitemap
from anime.models import Anime

class AnimeSitemap(Sitemap):
    priority = 1
    changefreq = "yearly"

    def items(self):
        return Anime.objects.all()

    def lastmod(self, obj):
        return obj.updated