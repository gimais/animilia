from django.contrib import admin
from .models import Comment,Profile

# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'body', 'anime', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ['user__username','body']
    actions = ['active_comments','inactive_comments']

    def active_comments(self, request, queryset):
        queryset.update(active=True)

    def inactive_comments(self, request, queryset):
        queryset.update(active=False)

admin.site.register(Comment,CommentAdmin)
admin.site.register(Profile)