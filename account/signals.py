from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from feedback.models import Message
from .models import Profile, Settings, Reply, Notification

User = get_user_model()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_and_settings(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Settings.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile_and_settings(sender, instance, **kwargs):
    instance.profile.save()
    instance.settings.save()


@receiver(post_save, sender=Reply)
def send_reply_notification(sender, instance, **kwargs):
    to_user = instance.to_comment.user
    if to_user != instance.reply_comment.user:
        Notification.objects.create(user=to_user, content_object=instance)


@receiver(post_save, sender=Message)
def send_message_notification(sender, instance, created,**kwargs):
    if created:
        if not instance.to_everyone:
            Notification.objects.create(user=instance.to_user, content_object=instance)
        else:
            notiications_for_everyone = []
            for user in User.objects.all():
                notiications_for_everyone.append(Notification(user=user,content_object=instance))
            Notification.objects.bulk_create(notiications_for_everyone)
