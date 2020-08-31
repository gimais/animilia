from datetime import datetime,timedelta
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count,Exists,OuterRef,Subquery
from django.utils import timezone
from anime.models import Anime


class CommentManager(models.Manager):
    def with_annotates_auth(self,user_pk):
        profiles = Profile.objects.filter(user_id=OuterRef('user_id'))
        user = User.objects.filter(pk=OuterRef('user_id'))
        has_like = User.objects.get(pk=user_pk).likes.filter(id=OuterRef('id'))
        has_dislike = User.objects.get(pk=user_pk).dislikes.filter(id=OuterRef('id'))
        return self.get_queryset().annotate(avatar=Subquery(profiles.values('avatar')[:1]),
                                            username=Subquery(user.values('username')[:1]),
                                            has_like=Exists(has_like),
                                            has_dislike=Exists(has_dislike),
                                            like_count=Count('like',distinct=True),
                                            dislike_count=Count('dislike', distinct=True),
                                            replies_count=Count('replies'))

    def with_annotates_anony(self):
        profiles = Profile.objects.filter(user_id=OuterRef('user_id'))
        user = User.objects.filter(pk=OuterRef('user_id'))
        return self.get_queryset().annotate(avatar=Subquery(profiles.values('avatar')[:1]),
                                            username=Subquery(user.values('username')[:1]),
                                            like_count=Count('like', distinct=True),
                                            dislike_count=Count('dislike', distinct=True),
                                            replies_count=Count('replies'))

class Comment(models.Model):
    anime = models.ForeignKey(Anime,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='comment')
    body = models.TextField()
    like = models.ManyToManyField(User,blank=True,editable=False,related_name='likes')
    dislike = models.ManyToManyField(User,blank=True,editable=False,related_name='dislikes')
    # spoiler = models.BooleanField(default=False)
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
            # 'has_spoiler': self.spoiler,
            'likes': self.like.count(),
            'dislikes': self.dislike.count(),
            'childs_count':self.replies.count(),
            'voted': vote,
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
                # 'has_spoiler':self.spoiler,
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


    def get_comments_count(self):
        return Comment.objects.filter(user=self.user).count()

    def __str__(self):
        return '{}-ის პროფილი'.format(self.user.username)


def sub_three_days():
    return timezone.now() - timedelta(days=3)

class Settings(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    username_updated = models.DateTimeField(auto_now_add=True)
    avatar_updated = models.DateTimeField(default=sub_three_days)
    show_birth = models.BooleanField(default=False)
    show_gender = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'პარამეტრები'
        verbose_name_plural = "პარამეტრები"

    def __str__(self):
        return "{}-ის პარამეტრები".format(self.user.username)