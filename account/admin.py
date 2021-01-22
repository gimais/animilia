from django.contrib import admin
from django.utils.html import format_html

from .models import Comment, Profile, Settings, Notification


# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'user', 'anime', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ['user__username', 'body']
    actions = ('active_comments', 'inactive_comments')
    readonly_fields = ('created', 'user', 'anime', 'parent_link')
    exclude = ('parent',)
    ordering = ('-id',)

    def get_exclude(self, request, obj=None):
        excluded = super().get_exclude(request, obj)

        if not request.user.is_superuser:
            return excluded + ('priority',)
        return excluded

    def get_list_display(self, request):
        list_display = super().get_list_display(request)

        if request.user.is_superuser:
            return list_display + ('priority',)
        return list_display

    def parent_link(self, obj=None):
        if obj.parent:
            return format_html("<a href='/admin/account/comment/{}/change/'>ლინკი</a>".format(obj.parent))
        return 'არ არსებობს!'

    def has_add_permission(self, request, obj=None):
        return False

    def active_comments(self, request, queryset):
        queryset.update(active=True)

    def inactive_comments(self, request, queryset):
        queryset.update(active=False)

    parent_link.short_description = 'მთავარი კომენტარი'


class ProfileAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ['user__username', ]
    list_display = ('user', 'gender', 'birth', 'profile_preview')
    readonly_fields = ('id', 'user', 'gender', 'birth')

    def has_add_permission(self, request, obj=None):
        return False

    def profile_preview(self, obj):
        return format_html('<a href="/profile/{}">საიტზე ნახვა</a>', obj.id)

    profile_preview.allow_tags = True


class SettingsAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('user', 'ip', 'comment_count', 'like_count', 'dislike_count')
    search_fields = ['user__username', 'ip']
    readonly_fields = ('id', 'user', 'ip', 'show_birth', 'show_gender', 'changed_avatar', 'changed_username')

    def has_add_permission(self, request, obj=None):
        return False

    def comment_count(self, obj):
        return obj.user.comment.count()

    def like_count(self, obj):
        return obj.user.likes.count()

    def dislike_count(self, obj):
        return obj.user.dislikes.count()

    def get_queryset(self, request):
        queryset = super(SettingsAdmin, self).get_queryset(request)
        queryset = queryset.prefetch_related('user__comment', 'user__likes', 'user__dislikes')
        return queryset


class NotificationAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'user', 'comment', 'reply_comment', 'comment_preview', 'reply_preview', 'visited')
    readonly_fields = ('id', 'user', 'comment', 'reply_comment')

    def has_add_permission(self, request, obj=None):
        return False

    def comment_preview(self, obj):
        return format_html("<a href='/admin/account/comment/{}/change/'>ლინკი</a>".format(obj.comment))

    def reply_preview(self, obj):
        return format_html("<a href='/admin/account/comment/{}/change/'>ლინკი</a>".format(obj.reply_comment))

    comment_preview.allow_tags = True
    reply_preview.allow_tags = True


admin.site.register(Comment, CommentAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Settings, SettingsAdmin)
admin.site.register(Notification, NotificationAdmin)
