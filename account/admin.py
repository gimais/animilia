from django.contrib import admin
from django.utils.html import format_html
from .models import Comment,Profile

# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'anime', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ['user__username','body']
    actions = ('active_comments','inactive_comments')
    readonly_fields = ('id','created','user','anime','parent_link')
    exclude = ['parent']

    def parent_link(self,obj=None):
        if obj.parent:
            return format_html("<a href='/admin/account/comment/{}/change/'>ლინკი</a>".format(obj.parent))
        return 'არ არსებობს!'

    def has_add_permission(self, request, obj=None):
        return False

    def active_comments(self, request, queryset):
        queryset.update(active=True)

    def inactive_comments(self, request, queryset):
        queryset.update(active=False)

    parent_link.short_description = 'Parent'

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user','gender','birth')
    readonly_fields = ('id','user','gender','birth')

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(Comment,CommentAdmin)
admin.site.register(Profile,ProfileAdmin)