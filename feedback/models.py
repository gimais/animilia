from account.models import User
from django.db import models


# Create your models here.


class Feedback(models.Model):
    customer_name = models.CharField(max_length=120, verbose_name='სახელი')
    email = models.EmailField()
    details = models.TextField(verbose_name='წერილი')
    date = models.DateTimeField(auto_now_add=True, verbose_name="თარიღი")
    ip = models.GenericIPAddressField(verbose_name='IP')
    closed = models.BooleanField(default=False, verbose_name='დახურული')
    registered_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "feedback"
        verbose_name = 'კონტაქტი'
        verbose_name_plural = 'კონტაქტი'

    def __str__(self):
        return str(self.pk)
