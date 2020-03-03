from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
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
        ordering = ['-created']
        verbose_name = 'კომენტარი'
        verbose_name_plural = 'კომენტარი'

    def get_reply_comment_info(self):

        if self.active:
            return {
                'comment_id':self.pk,
                'user_id':self.user.pk,
                'username':self.user.username,
                'user_avatar':'aq iqneba avatar',
                'time':datetime.timestamp(self.created),
                'parent_id':self.parent.pk,
                'body':self.body,
                'has_spoiler':self.spoiler,
                'likes':self.like.count(),
                'dislikes':self.dislike.count(),
                # 'vote_permission':
            }
        else:
            return {
                # 'user_id':self.user.pk,
                'deleted':True,
                'username':self.user.username,
                'user_avatar':'aq iqneba avatar',
                'time':datetime.timestamp(self.created),
            }

    def __str__(self):
        return '{}-ის კომენტარი'.format(self.user)