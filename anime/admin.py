from django.contrib import admin
from django.forms import CheckboxSelectMultiple

from .models import *

# Register your models here.


class AnimeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    list_display = ("name", "type",'slug','updated')

class AnimeSeriesAdmin(admin.ModelAdmin):
    list_display = ("anime", "url","row")
    list_filter = ("anime",)
    exclude = ('row',)

    class Media:
        js = ('/static/admin/js/hide_attribute.js',)


admin.site.register(Category)
admin.site.register(Anime,AnimeAdmin)
admin.site.register(AnimeSeries,AnimeSeriesAdmin)