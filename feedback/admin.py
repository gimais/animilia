from django.contrib import admin
from django.db import models
from django.forms import HiddenInput
from django.utils.html import format_html

from .forms import FeedbackReplyForm
from .models import Feedback, Message


# Register your models here.

def ReplyToFeedbackInline(obj):
    class Inline(admin.StackedInline):
        model = Message
        extra = 1
        max_num = 1
        form = FeedbackReplyForm(obj)
        verbose_name = 'პასუხი'
        formfield_overrides = {
            models.ForeignKey: {'widget': HiddenInput},
        }

    return Inline


class FeedbackAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ('id', 'ip', 'customer_name', 'date', 'closed', 'registered_user_link')
    list_filter = ('date', 'closed')
    search_fields = ('ip', 'body',)
    readonly_fields = ('id', 'date', 'ip', 'customer_name', 'email', 'registered_user', 'body')
    inlines = ()

    def get_fields(self, request, obj=None):
        if obj.registered_user is not None:
            return 'closed', 'id', 'date', 'ip', 'registered_user', 'email', 'body',
        return 'closed', 'id', 'date', 'ip', 'customer_name', 'email', 'body',

    def get_inline_instances(self, request, obj=None):
        if obj.registered_user is not None:
            return [inline(self.model, self.admin_site) for inline in self.inlines]
        return []

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = (ReplyToFeedbackInline(Feedback.objects.get(id=object_id)),)
        return super(FeedbackAdmin, self).change_view(request, object_id)

    def has_add_permission(self, request, obj=None):
        return False

    def registered_user_link(self, obj):
        if obj.registered_user:
            return format_html('<a href="/admin/account/profile/{}/change/">{}</a>', obj.registered_user.pk,
                               obj.registered_user)
        return 'ანონიმურია'

    def get_queryset(self, request):
        queryset = super(FeedbackAdmin, self).get_queryset(request)
        return queryset.select_related('registered_user')

    registered_user_link.short_description = "მომხმარებელი"


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'to_user', 'subject', 'created')
    fields = ('subject', 'body')
    search_fields = ('subject', 'to_user', )

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Message, MessageAdmin)
