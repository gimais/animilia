from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin, Group
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Count, Exists, OuterRef, Subquery, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from account.validators import MyASCIIUsernameValidator, OnlyDigitUsernameValidator, WebDomainValidator
from anime.models import Anime


class CustomUserManager(BaseUserManager):

    def with_user_details(self):
        return self.get_queryset().select_related('profile', 'settings').prefetch_related('groups')

    def create_user(self, username, email, password, is_staff=False, is_superuser=False, **extra_fields):
        if not username:
            raise ValueError(_('The given username must be set'))
        if not email:
            raise ValueError(_('The given email must be set'))

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        return self.create_user(username, email, password, True, True, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(**{'{}__iexact'.format(self.model.USERNAME_FIELD): username})


class CommentManager(models.Manager):
    def annotates_related_objects(self, user_obj):
        profiles = Profile.objects.filter(user_id=OuterRef('user_id'))
        user = get_user_model().objects.filter(pk=OuterRef('user_id'))

        params = {
            'user_active': Subquery(user.values('is_active')[:1]),
            'avatar': Subquery(profiles.values('avatar')[:1]),
            'username': Subquery(user.values('username')[:1]),
            'ui_class': Subquery(profiles.values('ui_class')[:1]),
            'like_count': Count('like', distinct=True),
            'dislike_count': Count('dislike', distinct=True),
            'children_count': Count('children', distinct=True),
            'active_children_count': Count('children', filter=Q(children__active=True), distinct=True)
        }

        if user_obj.is_authenticated:
            has_like = user_obj.likes.filter(id=OuterRef('id'))
            has_dislike = user_obj.dislikes.filter(id=OuterRef('id'))

            params['has_like'] = Exists(has_like)
            params['has_dislike'] = Exists(has_dislike)

        return self.get_queryset().annotate(**params)


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = MyASCIIUsernameValidator()
    username_min_length = MinLengthValidator(3)
    digits_validator = OnlyDigitUsernameValidator()

    username = models.CharField(
        max_length=16,
        unique=True,
        validators=[username_validator, username_min_length, digits_validator],
        verbose_name='ნიკი'
    )

    email = models.EmailField(unique=True, verbose_name='Email')

    is_staff = models.BooleanField(
        default=False,
        verbose_name='თანამშრომლობის სტატუსი'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='აქტიურია'
    )

    date_joined = models.DateTimeField(default=timezone.now, verbose_name='გაწევრიანების თარიღი')

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = "user"

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def get_notification_count(self):
        return self.notifications.filter(seen=False).count()


class Comment(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='comments', verbose_name='გვერდი')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment',
                             verbose_name='მომხმარებელი')
    body = models.TextField(verbose_name='ტექსტი')
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, editable=False, related_name='likes')
    dislike = models.ManyToManyField(settings.AUTH_USER_MODEL, editable=False, related_name='dislikes')
    created = models.DateTimeField(auto_now_add=True, verbose_name='თარიღი')
    active = models.BooleanField(default=True, verbose_name='აქტიურია')
    priority = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='პრიორიტეტი')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    objects = CommentManager()

    class Meta:
        permissions = [
            ("view_all_comment", "ყველა კომენტარის ნახვის უფლება"),
            ("edit_comment_text", "ტექსტის შეცვლის უფლება"),
            ("set_priority", "პრიორიტეტის მინიჭება (აპივნა)"),
        ]

        ordering = ['priority', '-id']
        verbose_name = 'კომენტარი'
        verbose_name_plural = 'კომენტარი'
        db_table = "comment"

    def get_more_comment_info(self, request_user):
        response = {
            'comment_id': self.pk,
            'user_id': self.user.pk,
            'user_active': self.user.is_active,
            'username': self.user.username,
            'ui_class': self.user.profile.ui_class,
            'avatar': self.user.profile.avatar.name,
            'time': datetime.timestamp(self.created),
            'body': self.body,
            'likes': self.like.count(),
            'dislikes': self.dislike.count(),
            'children_count': self.children.count(),
            'active_children_count': self.children.filter(active=True).count(),
        }

        if request_user.is_authenticated:
            if self.like.filter(pk=request_user.id).exists():
                response['voted'] = 0
            elif self.dislike.filter(pk=request_user.id).exists():
                response['voted'] = 1
            else:
                response['voted'] = None
        return response

    def get_deleted_comment_info(self):
        return {
            'deleted': True,
            'comment_id': self.id,
            'user_id': self.user.id,
            'user_active': self.user.is_active,
            'username': self.user.username,
            'ui_class': self.user.profile.ui_class,
            'avatar': self.user.profile.avatar.name,
            'time': datetime.timestamp(self.created),
            'children_count': self.children.count(),
            'active_children_count': self.children.filter(active=True).count(),
        }

    def get_reply_comment_info(self, request_user):
        if self.active:
            response = {
                'comment_id': self.pk,
                'parent_id': self.parent.pk,
                'user_id': self.user.pk,
                'user_active': self.user.is_active,
                'username': self.user.username,
                'ui_class': self.user.profile.ui_class,
                'avatar': self.user.profile.avatar.name,
                'time': datetime.timestamp(self.created),
                'body': self.body,
                'likes': self.like.count(),
                'dislikes': self.dislike.count(),
            }

            if self.user == request_user:
                response['editable'] = self.replies.exclude(reply_comment__user=request_user).count() == 0
            elif request_user.is_authenticated:
                if self.like.filter(pk=request_user.id).exists():
                    response['voted'] = 0
                elif self.dislike.filter(pk=request_user.id).exists():
                    response['voted'] = 1
                else:
                    response['voted'] = None
            return response
        else:
            return {
                'deleted': True,
                'username': self.user.username,
                'ui_class': self.user.profile.ui_class,
                'avatar': self.user.profile.avatar.name,
                'time': datetime.timestamp(self.created),
                'user_id': self.user.pk,
                'user_active': self.user.is_active
            }

    def __str__(self):
        return str(self.pk)


class Profile(models.Model):
    TYPES = (
        (0, 'მამრობითი'),
        (1, 'მდედრობითი')
    )
    facebook_validator = WebDomainValidator(['facebook', 'fb'], 'Facebook')
    instagram_validator = WebDomainValidator(['instagr', 'instagram'], 'Instagram')

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    avatar = models.ImageField(upload_to='avatars/', default='no-avatar.jpg', blank=True, verbose_name='ავატარი')
    gender = models.PositiveSmallIntegerField(choices=TYPES, blank=True, null=True, verbose_name='სქესი')
    birth = models.DateField(blank=True, null=True, verbose_name='დაბადების თარიღი')
    facebook = models.URLField(blank=True, null=True, validators=[facebook_validator])
    instagram = models.URLField(blank=True, null=True, validators=[instagram_validator])
    ui_class = models.CharField(blank=True, null=True, max_length=16, verbose_name="UI კლასი")

    class Meta:
        verbose_name = 'პროფილი'
        verbose_name_plural = "პროფილი"
        db_table = 'user_profile'

    def __str__(self):
        return '{}-ის პროფილი'.format(self.user.username)


def sub_three_days():
    return timezone.now() - timedelta(days=3)


def sub_seven_days():
    return timezone.now() - timedelta(days=7)


class Settings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    ip = models.GenericIPAddressField(verbose_name='IP', null=True)
    username_updated = models.DateTimeField(default=sub_seven_days)
    avatar_updated = models.DateTimeField(default=sub_three_days)
    show_birth = models.BooleanField(default=False)
    show_gender = models.BooleanField(default=False)
    changed_avatar = models.PositiveSmallIntegerField(default=0)
    changed_username = models.PositiveSmallIntegerField(default=0)

    class Meta:
        permissions = [
            ("staff_tools", "სტაფის ინსტრუმენტები"),
        ]

        verbose_name = 'პარამეტრი'
        verbose_name_plural = "პარამეტრები"
        db_table = 'user_settings'

    def __str__(self):
        return "{}-ის პარამეტრები".format(self.user.username)


class Reply(models.Model):
    to_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    reply_comment = models.ForeignKey(Comment, blank=True, on_delete=models.CASCADE)
    notification = GenericRelation('Notification', related_query_name='reply')

    class Meta:
        verbose_name = 'კომენტარზე პასუხი'
        verbose_name_plural = "კომენტარზე პასუხები"
        db_table = 'comment_reply'
        unique_together = ('to_comment', 'reply_comment')

    def __str__(self):
        return str(self.id)


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    seen = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'შეტყობინება'
        verbose_name_plural = "შეტყობინებები"
        db_table = 'user_notification'

    def __str__(self):
        return "user: {}, id: {}".format(self.user.username, self.id)


Group.add_to_class('display_color', models.CharField(max_length=7, null=True))
