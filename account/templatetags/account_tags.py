from django import template
from datetime import datetime, timedelta


def date_to_timestamp(date, val=0):
    return datetime.timestamp(date + timedelta(days=val))


def notif_count(user):
    return user.notification_set.filter(visited=False).count()


def geo_number(number):
    if 1 < number < 21 or number % 20 == 0:
        return 'მე-{}'.format(number)
    elif number == 1:
        return 'პირველი'
    else:
        return '{}-ე'.format(number)


register = template.Library()

register.filter(date_to_timestamp)
register.filter(notif_count)
register.filter(geo_number, is_safe=True)
