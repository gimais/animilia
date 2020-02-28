from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple
from .models import Category, Anime, AnimeSeries,Comment

# Register your models here.

admin.site.site_header = 'Admin Panel'
admin.site.site_title = "სამართავი პანელი"


class ChoiceInline(admin.TabularInline):
    model = AnimeSeries
    extra = 1


class AnimeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    list_display = ("name",'dubbed', "type", 'slug', 'updated')
    inlines = [ChoiceInline]


class AnimeSeriesAdmin(admin.ModelAdmin):
    list_display = ("anime", "url","row")
    list_filter = ("anime",)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "posts",)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'body', 'anime', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ('user', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

admin.site.register(Category,CategoryAdmin)
admin.site.register(Anime, AnimeAdmin)
admin.site.register(Comment,CommentAdmin)