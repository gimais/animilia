from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from .models import Category, Anime, Video, Dubber, Schedule, WatchOrder, WatchingOrderingGroup


# Register your models here.


class VideoChoiceInline(admin.TabularInline):
    model = Video
    extra = 1


class OrderChoiceInline(admin.TabularInline):
    model = WatchOrder
    extra = 1


class AnimeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    list_display = ("name", 'dubbed', "type", 'slug', 'updated', 'finished')
    inlines = [VideoChoiceInline]

    fieldsets = (
        ('სახელები', {'fields': ('name', 'namege', 'nameen', 'namejp', 'nameru')}),
        ('დეტალები', {'fields': ('director', 'studio', 'year', 'age', 'categories',
                                 'type', 'episodes', 'rating', 'poster', 'description')}),
        ('ანიმილია', {'fields': ('dubbers', 'slug', 'finished', 'soon')}),
    )

    class Media:
        js = ('admin/js/extrasett.js',)


class ScheduleAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'anime':
            kwargs["queryset"] = Anime.objects.filter(finished=False)
        return super(ScheduleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class WatchingOrderingAdmin(admin.ModelAdmin):
    inlines = [OrderChoiceInline]


admin.site.register(Category)
admin.site.register(Dubber)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(WatchingOrderingGroup, WatchingOrderingAdmin)
admin.site.register(Anime, AnimeAdmin)
