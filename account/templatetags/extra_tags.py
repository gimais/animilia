from datetime import datetime, timedelta

from django import template


def date_to_timestamp(date, val=0):
    return datetime.timestamp(date + timedelta(days=val))


def access_collection_element(collection, index):
    return collection[index]


def geo_number(number):
    if 1 < number < 21 or number % 20 == 0:
        return 'მე-{}'.format(number)
    elif number == 1:
        return 'პირველი'
    else:
        return '{}-ე'.format(number)


def is_member_of(user, group_name):
    return user.groups.filter(name=group_name).exists()


register = template.Library()

register.filter(date_to_timestamp)
register.filter(is_member_of)
register.filter(access_collection_element)
register.filter(geo_number, is_safe=True)
