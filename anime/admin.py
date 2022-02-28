from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple, NumberInput

from staff.admin import staff_site, admin_site
from .models import Category, Anime, Video, Dubber, Schedule, Chronology, ChronologyItem


class VideoChoiceInline(admin.TabularInline):
    model = Video
    extra = 1

    def get_max_num(self, request, obj=None, **kwargs):
        if obj is not None and (obj.type == 1 or obj.type == 4):
            return 1
        return self.max_num

    def get_queryset(self, request):
        queryset = super(VideoChoiceInline, self).get_queryset(request)
        return queryset.select_related('anime')


class ChronologySequenceInline(admin.TabularInline):
    model = ChronologyItem
    extra = 1


class ChronologyAdmin(admin.ModelAdmin):
    inlines = [ChronologySequenceInline]


class DubberAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.OneToOneField: {'widget': NumberInput},
    }


class AnimeStaff(admin.ModelAdmin):
    view_on_site = False
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    list_display = ("name", 'dubbed', "type", 'updated', 'status')
    inlines = [VideoChoiceInline]

    fieldsets = (
        ('სახელები', {'fields': ('name', 'namege', 'nameen', 'namejp', 'nameru')}),
        ('დეტალები', {'fields': ('director', 'studio', 'year', 'age', 'categories',
                                 'type', 'episodes', 'rating', 'poster', 'description')}),
        ('Animilia', {'fields': ('dubbers', 'slug', 'status', 'soon', 'deleted')}),
    )

    def get_queryset(self, request):
        queryset = super(AnimeStaff, self).get_queryset(request)
        queryset = queryset.prefetch_related('videos')

        if request.user.has_perm('anime.view_all_anime'):
            return queryset

        try:
            return request.user.dubber.get_dubbed_animes
        except Dubber.DoesNotExist:
            return Schedule.objects.none()


class ScheduleStaff(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'anime':
            if request.user.has_perm('anime.view_all_schedule'):
                kwargs["queryset"] = Anime.objects.filter(status__in=[1, 2], deleted=False)
            else:
                try:
                    kwargs["queryset"] = request.user.dubber.get_dubbed_animes.filter(status__in=[1, 2], deleted=False)
                except Dubber.DoesNotExist:
                    kwargs["queryset"] = Anime.objects.none()
        return super(ScheduleStaff, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        queryset = super(ScheduleStaff, self).get_queryset(request)
        queryset = queryset.select_related('anime')

        if request.user.has_perm('anime.view_all_schedule'):
            return queryset

        try:
            return queryset.filter(anime__in=request.user.dubber.get_dubbed_animes)
        except Dubber.DoesNotExist:
            return Schedule.objects.none()


class ScheduleAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'anime':
            kwargs["queryset"] = Anime.objects.filter(status__in=[1, 2], deleted=False)
        return super(ScheduleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        queryset = super(ScheduleAdmin, self).get_queryset(request)
        queryset = queryset.select_related('anime')
        return queryset


staff_site.register(Category)
staff_site.register(Schedule, ScheduleStaff)
staff_site.register(Anime, AnimeStaff)
staff_site.register(Chronology, ChronologyAdmin)
staff_site.register(Dubber, DubberAdmin)

admin_site.register(Category)
admin_site.register(Dubber, DubberAdmin)
admin_site.register(Schedule, ScheduleAdmin)
admin_site.register(Chronology, ChronologyAdmin)
admin_site.register(Anime, AnimeStaff)
