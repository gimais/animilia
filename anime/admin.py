from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple, NumberInput

from staff.admin import staff_site, admin_site
from .models import Category, Anime, Video, Dubber, Schedule, WatchOrder, WatchingOrderingGroup


# Register your models here.


class VideoChoiceInline(admin.TabularInline):
    model = Video
    extra = 1


class OrderChoiceInline(admin.TabularInline):
    model = WatchOrder
    extra = 1


class WatchingOrderingAdmin(admin.ModelAdmin):
    inlines = [OrderChoiceInline]


class DubberAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.OneToOneField: {'widget': NumberInput},
    }


class AnimeStaff(admin.ModelAdmin):
    view_on_site = False
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

    def get_queryset(self, request):
        queryset = super(AnimeStaff, self).get_queryset(request)

        if request.user.has_perm('anime.view_all_anime'):
            return queryset

        return request.user.dubber.get_dubbed_animes


class ScheduleStaff(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'anime':
            if request.user.has_perm('anime.view_all_schedule'):
                kwargs["queryset"] = Anime.objects.filter(finished=False)
            else:
                kwargs["queryset"] = request.user.dubber.get_dubbed_animes.filter(finished=False)
        return super(ScheduleStaff, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        queryset = super(ScheduleStaff, self).get_queryset(request)

        if request.user.has_perm('anime.view_all_schedule'):
            return queryset

        return queryset.filter(anime__in=request.user.dubber.get_dubbed_animes)


staff_site.register(Category)
staff_site.register(Schedule, ScheduleStaff)
staff_site.register(Anime, AnimeStaff)
staff_site.register(WatchingOrderingGroup, WatchingOrderingAdmin)

admin_site.register(Dubber, DubberAdmin)
admin_site.register(WatchingOrderingGroup, WatchingOrderingAdmin)
admin_site.register(Anime, AnimeStaff)
