from datetime import datetime,timedelta
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Exists, OuterRef, Subquery
from django.utils import timezone
from anime.models import Anime

class CommentManager(models.Manager):
    def with_annotates(self,user_obj):
        profiles = Profile.objects.filter(user_id=OuterRef('user_id'))
        user = User.objects.filter(pk=OuterRef('user_id'))
        params = {'avatar' : Subquery(profiles.values('avatar')[:1]),
                  'username' : Subquery(user.values('username')[:1]),
                  'like_count' : Count('like',distinct=True),
                  'dislike_count' : Count('dislike', distinct=True),
                  'replies_count' : Count('replies',distinct=True)}

        if user_obj.is_authenticated:
            has_like = user_obj.likes.filter(id=OuterRef('id'))
            has_dislike = user_obj.dislikes.filter(id=OuterRef('id'))

            params['has_like'] = Exists(has_like)
            params['has_dislike'] = Exists(has_dislike)

        return self.get_queryset().annotate(**params)

class Comment(models.Model):
    anime = models.ForeignKey(Anime,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='comment')
    body = models.TextField()
    like = models.ManyToManyField(User,blank=True,editable=False,related_name='likes')
    dislike = models.ManyToManyField(User,blank=True,editable=False,related_name='dislikes')
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='replies')

    objects = CommentManager()

    class Meta:
        ordering = ['-id']
        verbose_name = 'კომენტარი'
        verbose_name_plural = 'კომენტარი'

    def get_more_comment_info(self,request_user):
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
            'childs_count':self.replies.count(),
            'voted': vote,
        }

    def get_deleted_comment_for_notification_redirect(self):
        return {
            'comment_id': self.pk,
            'user_id': self.user.pk,
            'username': self.user.username,
            'avatar': self.user.profile.avatar.name,
            'time': datetime.timestamp(self.created),
            'childs_count':self.replies.count(),
        }

    def get_reply_comment_info(self,request_user):
        vote = None
        if self.like.filter(pk=request_user).exists():
            vote = 0
        elif self.dislike.filter(pk=request_user).exists():
            vote = 1

        if self.active:
            return {
                'comment_id':self.pk,
                'user_id':self.user.pk,
                'username':self.user.username,
                'avatar':self.user.profile.avatar.name,
                'time':datetime.timestamp(self.created),
                'parent_id':self.parent.pk,
                'body':self.body,
                'likes':self.like.count(),
                'dislikes':self.dislike.count(),
                'voted': vote,
            }
        else:
            return {
                'deleted':True,
                'username':self.user.username,
                'avatar':self.user.profile.avatar.name,
                'time':datetime.timestamp(self.created),
                'user_id':self.user.pk
            }

    def __str__(self):
        return str(self.pk)

class Profile(models.Model):
    TYPES = (
        (0,'მამრობითი'),
        (1,'მდედრობითი')
    )

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/',default='no-avatar.jpg',blank=True,verbose_name='ავატარი')
    gender = models.PositiveSmallIntegerField(choices=TYPES,blank=True,null=True,verbose_name='სქესი')
    birth = models.DateField(blank=True,null=True,verbose_name='დაბადების თარიღი')


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
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(verbose_name='IP',null=True)
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
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE,related_name='notifications')
    reply_comment = models.ForeignKey(Comment,blank=True,on_delete=models.CASCADE)

    def __str__(self):
        return "comment_id: {}, reply_id: {}, user_id : {}".format(self.comment.id,self.reply_comment.id,self.user.username)