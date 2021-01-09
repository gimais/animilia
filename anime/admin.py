from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from .models import Category, Anime, Video, Dubber, Schedule


# Register your models here.


class ChoiceInline(admin.TabularInline):
    model = Video
    extra = 1


class AnimeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    list_display = ("name", 'dubbed', "type", 'slug', 'updated', 'finished')
    inlines = [ChoiceInline]

    fieldsets = (
        ('სახელები', {'fields': ('name', 'namege', 'nameen', 'namejp', 'nameru')}),
        ('დეტალები', {'fields': ('director', 'studio', 'year', 'age', 'categories',
                                 'type', 'episodes', 'rating', 'poster', 'description')}),
        ('ანიმილია', {'fields': ('dubbers', 'slug', 'finished', 'soon')}),
    )

    class Media:
        js = ('admin/js/extrasett.js',)


admin.site.register(Category)
admin.site.register(Dubber)
admin.site.register(Schedule)
admin.site.register(Anime, AnimeAdmin)
