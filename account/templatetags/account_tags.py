from django import template
from datetime import datetime,timedelta

def date_to_timestamp(date,val=0):
    return datetime.timestamp(date+timedelta(days=val))

def notif_count(user):
    return user.notification_set.filter(visited=False).count()

register = template.Library()

register.filter(date_to_timestamp)
register.filter(notif_count)