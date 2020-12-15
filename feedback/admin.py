from django.contrib import admin
from django.utils.html import format_html

from .models import Feedback


# Register your models here.

class FeedbackAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ('id', 'ip', 'customer_name', 'date', 'closed', 'registered_user_link')
    list_filter = ('date', 'closed')
    search_fields = ('ip', 'details',)
    readonly_fields = ('id', 'date', 'ip', 'customer_name', 'email', 'details')
    exclude = ['registered_user']

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


admin.site.register(Feedback, FeedbackAdmin)
