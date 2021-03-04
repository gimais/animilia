from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class StaffConfig(AppConfig):
    name = 'staff'
    verbose_name = 'სტაფი'


class StaffPanelConfig(AdminConfig):
    default_site = 'staff.admin.StaffSite'
