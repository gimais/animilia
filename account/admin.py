from django.contrib import admin
from django.utils.html import format_html
from .models import Comment, Profile, Settings


# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id','user', 'anime', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ['user__username','body']
    actions = ('active_comments','inactive_comments')
    readonly_fields = ('id','created','user','anime','parent_link','body')
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
    list_per_page = 20
    search_fields = ['user__username',]
    list_display = ('user','gender','birth','profile_preview')
    readonly_fields = ('id','user','gender','birth')

    def has_add_permission(self, request, obj=None):
        return False

    def profile_preview(self,obj):
        return format_html('<a href="/profile/{}">საიტზე ნახვა</a>',obj.id)

    profile_preview.allow_tags = True

class SettingsAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('user','ip','comment_count')
    readonly_fields = ('id','user','ip','show_birth','show_gender','avatar_updated','username_updated')

    def has_add_permission(self, request, obj=None):
        return False

    def comment_count(self,obj):
        return obj.user.comment.count()

    def get_queryset(self, request):
        queryset = super(SettingsAdmin, self).get_queryset(request)
        queryset = queryset.prefetch_related('user__comment')
        return queryset

admin.site.register(Comment,CommentAdmin)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(Settings,SettingsAdmin)