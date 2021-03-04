from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from anime.models import Dubber
from staff.admin import staff_site, admin_site
from .models import Comment, Profile, Settings, Notification, Reply

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'is_staff')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email')
    ordering = ('id',)

    def has_add_permission(self, request, obj=None):
        return False


class SettingsAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('user', 'ip', 'comment_count', 'like_count', 'dislike_count')
    search_fields = ['user__username', 'ip']
    readonly_fields = ('user', 'ip', 'show_birth', 'show_gender', 'changed_avatar', 'changed_username')

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
    list_display = ('id', 'user', 'content_type', 'object_id', 'seen')
    readonly_fields = ('id', 'user', 'content_type', 'object_id', 'seen')

    def has_add_permission(self, request, obj=None):
        return False


class ReplyAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'comment_preview', 'reply_preview')

    def has_add_permission(self, request, obj=None):
        return False

    def comment_preview(self, obj):
        return format_html("<a href='/admin/account/comment/{id}/change/'>{id}</a>".format(id=obj.to_comment))

    def reply_preview(self, obj):
        return format_html("<a href='/admin/account/comment/{id}/change/'>{id}</a>".format(id=obj.reply_comment))


class CommentStaff(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'user', 'anime', 'created', 'active')
    list_filter = ('created',)
    search_fields = ('user__username',)
    readonly_fields = ('created', 'user', 'anime', 'parent_link')
    exclude = ('parent', 'priority')
    ordering = ('-id',)

    def get_readonly_fields(self, request, obj=None):
        readonly = super(CommentStaff, self).get_readonly_fields(request, obj)

        if not request.user.has_perm('account.edit_comment_text'):
            return readonly + ('body',)

        return readonly

    def parent_link(self, obj=None):
        if obj.parent:
            return format_html("<a href='/staff/account/comment/{}/change/'>ლინკი</a>".format(obj.parent))
        return 'არ არსებობს!'

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        queryset = super(CommentStaff, self).get_queryset(request)
        queryset = queryset.prefetch_related('parent')

        if request.user.has_perm('account.view_all_comment'):
            return queryset

        try:
            return queryset.filter(anime__in=request.user.dubber.get_dubbed_animes)
        except Dubber.DoesNotExist:
            return Comment.objects.none()

    parent_link.short_description = 'მთავარი კომენტარი'


class CommentAdmin(CommentStaff):
    list_display = ('id', 'user', 'anime', 'created', 'active', 'priority')
    list_filter = ('active', 'created')
    search_fields = ('user__username', 'body')
    actions = ('active_comments', 'inactive_comments')
    readonly_fields = ('created', 'user', 'anime', 'parent_link')
    exclude = ('parent',)

    def active_comments(self, request, queryset):
        queryset.update(active=True)

    def inactive_comments(self, request, queryset):
        queryset.update(active=False)


class ProfileStaff(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('user__username',)
    list_display = ('user', 'gender', 'birth', 'profile_preview')
    readonly_fields = ('user', 'gender', 'birth')

    def has_add_permission(self, request, obj=None):
        return False

    def profile_preview(self, obj):
        return format_html('<a href="/profile/{}" target="_blank">საიტზე ნახვა</a>', obj.user_id)

    profile_preview.allow_tags = True


class ProfileAdmin(ProfileStaff):
    list_display = ('user', 'gender', 'birth', 'avatar', 'profile_preview')
    readonly_fields = ('user',)


staff_site.register(Comment, CommentStaff)
staff_site.register(Profile, ProfileStaff)

admin_site.register(Comment, CommentAdmin)
admin_site.register(Profile, ProfileAdmin)

admin_site.register(User, CustomUserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Settings, SettingsAdmin)
admin_site.register(Reply, ReplyAdmin)
admin_site.register(Notification, NotificationAdmin)
