from datetime import datetime,timedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from anime.models import Anime

class Comment(models.Model):
    anime = models.ForeignKey(Anime,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='users')
    body = models.TextField()
    like = models.ManyToManyField(User,blank=True,editable=False,related_name='likes')
    dislike = models.ManyToManyField(User,blank=True,editable=False,related_name='dislikes')
    spoiler = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='replies')

    class Meta:
        ordering = ['-id']
        verbose_name = 'კომენტარი'
        verbose_name_plural = 'კომენტარი'

    def get_more_comment_info(self):

        return {
            'comment_id': self.pk,
            'user_id': self.user.pk,
            'username': self.user.username,
            'avatar': self.user.profile.avatar.name,
            'time': datetime.timestamp(self.created),
            'body': self.body,
            'has_spoiler': self.spoiler,
            'likes': self.like.count(),
            'dislikes': self.dislike.count(),
            'childs_count':self.replies.count(),
        }

    def get_reply_comment_info(self):

        if self.active:
            return {
                'comment_id':self.pk,
                'user_id':self.user.pk,
                'username':self.user.username,
                'avatar':self.user.profile.avatar.name,
                'time':datetime.timestamp(self.created),
                'parent_id':self.parent.pk,
                'body':self.body,
                'has_spoiler':self.spoiler,
                'likes':self.like.count(),
                'dislikes':self.dislike.count(),
            }
        else:
            return {
                'deleted':True,
                'username':self.user.username,
                'avatar':self.user.profile.avatar.name,
                'time':datetime.timestamp(self.created),
            }

    def __str__(self):
        return '{}-ის კომენტარი'.format(self.user)



class Profile(models.Model):
    TYPES = (
        (0,'კაცი'),
        (1,'ქალი')
    )

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/',default='no-avatar.jpg',blank=True,verbose_name='ავატარი')
    # avatar_url = models.CharField(max_length=35,default='/static/img/no-avatar.jpg')
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
    email_updated = models.BooleanField(default=False)
    new_email = models.EmailField()

    class Meta:
        verbose_name = 'პარამეტრები'
        verbose_name_plural = "პარამეტრები"

    def __str__(self):
        return "{}-ის პარამეტრები".format(self.user.username)