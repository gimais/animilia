from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from .models import Category, Anime, AnimeSeries, Dubber, Schedule


# Register your models here.


class ChoiceInline(admin.TabularInline):
    model = AnimeSeries
    extra = 1


class AnimeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    list_display = ("name", 'dubbed', "type", 'slug', 'updated', 'finished')
    inlines = [ChoiceInline]

    class Media:
        js = ('admin/js/extrasett.js',)


admin.site.register(Category)
admin.site.register(Dubber)
admin.site.register(Schedule)
admin.site.register(Anime, AnimeAdmin)
