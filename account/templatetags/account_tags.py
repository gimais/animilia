from django import template
from datetime import datetime,timedelta


register = template.Library()

def date_to_timestamp(date,val=0):
    return datetime.timestamp(date+timedelta(days=val))

register.filter(date_to_timestamp)