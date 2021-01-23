from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

# Create your models here.
from account.models import Notification


class Feedback(models.Model):
    customer_name = models.CharField(max_length=120, verbose_name='სახელი')
    email = models.EmailField()
    body = models.CharField(verbose_name='წერილი', max_length=2000)
    date = models.DateTimeField(auto_now_add=True, verbose_name="თარიღი")
    ip = models.GenericIPAddressField(verbose_name='IP')
    closed = models.BooleanField(default=False, verbose_name='დახურული')
    registered_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                        verbose_name='მომხმარებელი')

    class Meta:
        db_table = "feedback"
        verbose_name = 'კონტაქტი'
        verbose_name_plural = 'კონტაქტი'

    def __str__(self):
        return str(self.pk)


class Message(models.Model):
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default=1,
                                related_name='messages', verbose_name='მომხმარებელი')
    feedback = models.ForeignKey(Feedback, on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.CharField(max_length=40, verbose_name='სათაური')
    body = models.TextField(verbose_name='ტექსტი')
    created = models.DateTimeField(auto_now_add=True)
    notification = GenericRelation(Notification, related_query_name='message')

    class Meta:
        db_table = 'message'
        verbose_name = 'წერილი'
        verbose_name_plural = 'წერილი'

    def __str__(self):
        return str(self.id)
