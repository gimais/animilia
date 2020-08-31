from django.contrib import admin
from django.utils.html import format_html

from .models import Feedback

# Register your models here.

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id','ip','customer_name', 'date','closed')
    list_filter = ('date','closed')
    search_fields = ('ip', 'details',)
    readonly_fields = ('id','date','ip', 'customer_name','email','details')

    def has_add_permission(self, request, obj=None):
        return False

    class Meta:
        model = Feedback

admin.site.register(Feedback, FeedbackAdmin)