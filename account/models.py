from datetime import datetime, timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import  AbstractUser, UserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.db.models import Count, Exists, OuterRef, Subquery, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from anime.models import Anime


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=16,
        unique=True,
        help_text=_('Required. 16 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
        verbose_name='ნიკი'
    )
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email',]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        swappable = "AUTH_USER_MODEL"
        db_table = "auth_user"

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class CommentManager(models.Manager):
    def related_objects_annotates(self, user_obj):
        profiles = Profile.objects.filter(user_id=OuterRef('user_id'))
        user = User.objects.filter(pk=OuterRef('user_id'))
        params = {'avatar': Subquery(profiles.values('avatar')[:1]),
                  'username': Subquery(user.values('username')[:1]),
                  'like_count': Count('like', distinct=True),
                  'dislike_count': Count('dislike', distinct=True),
                  'replies_count': Count('replies', distinct=True),
                  'active_replies_count': Count('replies', filter=Q(replies__active=True), distinct=True)}

        if user_obj.is_authenticated:
            has_like = user_obj.likes.filter(id=OuterRef('id'))
            has_dislike = user_obj.dislikes.filter(id=OuterRef('id'))

            params['has_like'] = Exists(has_like)
            params['has_dislike'] = Exists(has_dislike)

        return self.get_queryset().annotate(**params)


class Comment(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='comments', verbose_name='გვერდი')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment',
                             verbose_name='მომხმარებელი')
    body = models.TextField(verbose_name='ტექსტი')
    like = models.ManyToManyField(User, blank=True, editable=False, related_name='likes')
    dislike = models.ManyToManyField(User, blank=True, editable=False, related_name='dislikes')
    created = models.DateTimeField(auto_now_add=True, verbose_name='თარიღი')
    active = models.BooleanField(default=True, verbose_name='აქტიურია')
    priority = models.PositiveSmallIntegerField(null=True, verbose_name='პრიორიტეტი')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    objects = CommentManager()

    class Meta:
        ordering = ['priority', '-id']
        verbose_name = 'კომენტარი'
        verbose_name_plural = 'კომენტარი'

    def get_more_comment_info(self, request_user):
        vote = None
        if self.like.filter(pk=request_user).exists():
            vote = 0
        elif self.dislike.filter(pk=request_user).exists():
            vote = 1

        return {
            'comment_id': self.pk,
            'user_id': self.user.pk,
            'username': self.user.username,
            'avatar': self.user.profile.avatar.name,
            'time': datetime.timestamp(self.created),
            'body': self.body,
            'likes': self.like.count(),
            'dislikes': self.dislike.count(),
            'childs_count': self.replies.count(),
            'active_childs_count': self.replies.filter(active=True).count(),
            'voted': vote,
        }

    def get_deleted_comment_info(self):
        return {
            'deleted': True,
            'comment_id': self.id,
            'user_id': self.user.id,
            'username': self.user.username,
            'avatar': self.user.profile.avatar.name,
            'time': datetime.timestamp(self.created),
            'childs_count': self.replies.count(),
            'active_childs_count': self.replies.filter(active=True).count(),
        }

    def get_reply_comment_info(self, request_user=None):
        if self.active:
            vote = None
            if self.like.filter(pk=request_user).exists():
                vote = 0
            elif self.dislike.filter(pk=request_user).exists():
                vote = 1

            return {
                'comment_id': self.pk,
                'parent_id': self.parent.pk,
                'user_id': self.user.pk,
                'username': self.user.username,
                'avatar': self.user.profile.avatar.name,
                'time': datetime.timestamp(self.created),
                'body': self.body,
                'likes': self.like.count(),
                'dislikes': self.dislike.count(),
                'voted': vote,
            }
        else:
            return {
                'deleted': True,
                'username': self.user.username,
                'avatar': self.user.profile.avatar.name,
                'time': datetime.timestamp(self.created),
                'user_id': self.user.pk
            }

    def __str__(self):
        return str(self.pk)


class Profile(models.Model):
    TYPES = (
        (0, 'მამრობითი'),
        (1, 'მდედრობითი')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='no-avatar.jpg', blank=True, verbose_name='ავატარი')
    gender = models.PositiveSmallIntegerField(choices=TYPES, blank=True, null=True, verbose_name='სქესი')
    birth = models.DateField(blank=True, null=True, verbose_name='დაბადების თარიღი')

    class Meta:
        verbose_name = 'პროფილი'
        verbose_name_plural = "პროფილი"

    def __str__(self):
        return '{}-ის პროფილი'.format(self.user.username)


def sub_three_days():
    return timezone.now() - timedelta(days=3)


def sub_seven_days():
    return timezone.now() - timedelta(days=7)


class Settings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(verbose_name='IP', null=True)
    username_updated = models.DateTimeField(default=sub_seven_days)
    avatar_updated = models.DateTimeField(default=sub_three_days)
    show_birth = models.BooleanField(default=False)
    show_gender = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'პარამეტრი'
        verbose_name_plural = "პარამეტრები"

    def __str__(self):
        return "{}-ის პარამეტრები".format(self.user.username)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='notifications')
    reply_comment = models.ForeignKey(Comment, blank=True, on_delete=models.CASCADE)
    visited = models.BooleanField(default=False)

    def __str__(self):
        return "comment_id: {}, reply_id: {}, user_id : {}".format(self.comment.id, self.reply_comment.id,
                                                                   self.user.username)
