from datetime import datetime
from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=18,primary_key=True)
    # posts = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'categories'
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Anime(models.Model):
    TYPES = (
        (0,'სერიალი'),
        (1,'კინო')
    )

    name = models.CharField(max_length=100,unique=True,verbose_name='სახელი')
    nameen = models.CharField(max_length=100,verbose_name='ინგლისურად',blank=True)
    namejp = models.CharField(max_length=100,verbose_name='იაპონურად',blank=True)
    nameru = models.CharField(max_length=100,verbose_name='რუსულად',blank=True)
    dubber = models.CharField(max_length=16,verbose_name='გამხმოვანებელი',unique=False)
    poster = models.ImageField(upload_to='posters/',max_length=50,blank=True,verbose_name='სურათი')
    year = models.PositiveSmallIntegerField(verbose_name='გამოშვების წელი')
    director = models.CharField(max_length=40,verbose_name='რეჟისორი')
    studio = models.CharField(max_length=20,verbose_name='სტუდია')
    age = models.PositiveSmallIntegerField(verbose_name='შეზღუდვის ასაკი')
    description = models.TextField(verbose_name='აღწერა')
    categories = models.ManyToManyField(Category,related_name='categories',verbose_name='ჟანრები')
    type = models.PositiveSmallIntegerField(choices=TYPES,default=0,verbose_name='ტიპი')
    episodes = models.PositiveSmallIntegerField(verbose_name='ეპიზოდების რაოდენობა',default=1)
    # comments = models.PositiveSmallIntegerField()
    updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True,verbose_name='ლინკი')


    class Meta:
        db_table = 'animes_list'
        verbose_name = 'Anime'
        verbose_name_plural = 'Anime'

    def __str__(self):
        return self.name


class AnimeSeries(models.Model):
    anime = models.ForeignKey(Anime,on_delete=models.CASCADE,verbose_name='ანიმე',limit_choices_to={'type':0})
    url = models.CharField(max_length=60,verbose_name='ვიდეოს ლინკი')
    row = models.PositiveSmallIntegerField(default=1,verbose_name='მერამდენე ეპიზოდია')

    class Meta:
        db_table = 'animes_series'
        verbose_name = 'Anime Serie'
        verbose_name_plural = 'Anime Series'

    def save(self, *args, **kwargs):
        if self._state.adding:
            last_id = AnimeSeries.objects.filter(anime=self.anime).aggregate(largest=models.Max('row'))['largest']

            if last_id is not None:
                self.row = last_id + 1
        super(AnimeSeries, self).save(*args, **kwargs)

        Anime.objects.get(pk=self.anime.pk).updated = datetime.now() # update after adding episodes

        Anime.save(self.anime,update_fields=['updated'])

    def __str__(self):
        return '{} - {}'.format(self.anime,self.row)
