from django.contrib.admin import AdminSite


class SuperAdminSite(AdminSite):

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser


class StaffSite(AdminSite):
    site_title = 'Animilia'
    site_header = 'სტაფი'
    index_title = 'ადმინისტრირება'

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff


staff_site = StaffSite(name='staff')
admin_site = SuperAdminSite(name='admin')
