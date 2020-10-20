from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F

class Category(models.Model):
    name = models.CharField(max_length=18,unique=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'კატეგორია'
        verbose_name_plural = 'კატეგორიები'

    def __str__(self):
        return self.name

class Dubber(models.Model):
    name = models.CharField(max_length=16,unique=True)

    class Meta:
        db_table = 'dubbers'
        verbose_name = 'გამხმოვანებელი'
        verbose_name_plural = 'გამხმოვანებლები'

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
    dubbers = models.ManyToManyField(Dubber,related_name='dubbers',verbose_name='გამხმოვანებელი')
    poster = models.ImageField(upload_to='posters/',max_length=50,blank=True,verbose_name='სურათი')
    year = models.PositiveSmallIntegerField(verbose_name='გამოშვების წელი')
    director = models.CharField(max_length=45,verbose_name='რეჟისორი')
    studio = models.CharField(max_length=45,verbose_name='სტუდია')
    age = models.PositiveSmallIntegerField(verbose_name='შეზღუდვის ასაკი')
    description = models.TextField(verbose_name='აღწერა')
    categories = models.ManyToManyField(Category,related_name='categories',verbose_name='ჟანრები')
    type = models.PositiveSmallIntegerField(choices=TYPES,default=0,verbose_name='ტიპი')
    episodes = models.PositiveSmallIntegerField(verbose_name='ეპიზოდების რაოდენობა',default=1)
    rating = models.DecimalField(max_digits=5, decimal_places=1,default=0,verbose_name='რეიტინგი')
    updated = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0,editable=False)
    dubbed = models.PositiveSmallIntegerField(default=0,verbose_name='გახმოვანებული',editable=False)
    slug = models.SlugField(unique=True,verbose_name='ლინკი')
    finished = models.BooleanField(default=False,verbose_name="დამთავრებულია")

    class Meta:
        db_table = 'animes_list'
        verbose_name = 'ანიმე'
        verbose_name_plural = 'ანიმეები'

    def increase_view_count(self,cookies):
        if cookies.get('_vEpAd',False) == False:
            Anime.objects.filter(pk=self.pk).update(views=F('views') + 1)

    def save(self, *args, **kwargs):
        if self.type==1:
            self.episodes = 1

        super(Anime, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/anime/{self.slug}'

    def __str__(self):
        return self.name

class AnimeSeries(models.Model):
    anime = models.ForeignKey(Anime,on_delete=models.CASCADE,verbose_name='ანიმე',limit_choices_to={'type':0},related_name='series')
    url = models.CharField(max_length=100,verbose_name='ვიდეოს ლინკი')
    row = models.PositiveSmallIntegerField(default=1,verbose_name='მერამდენე ეპიზოდია',editable=False)

    class Meta:
        db_table = 'animes_series'
        verbose_name = 'ანიმე სერია'
        verbose_name_plural = 'ანიმე სერიები'

    def delete(self, using=None, keep_parents=False):
        super(AnimeSeries, self).delete()

        largest = AnimeSeries.objects.filter(anime=self.anime).aggregate(largest=models.Max('row'))['largest']
        Anime.objects.filter(pk=self.anime.pk).update(dubbed=largest)

    def save(self, *args, **kwargs):
        if self._state.adding:
            last_id = AnimeSeries.objects.filter(anime=self.anime).aggregate(largest=models.Max('row'))['largest']

            if self.anime.type==1 and last_id is not None:
                return

            if last_id is not None:
                self.row = last_id + 1

        super(AnimeSeries, self).save(*args, **kwargs)

        Anime.objects.get(pk=self.anime.pk).updated = datetime.now() # update after adding episodes

        Anime.save(self.anime)

        largest = AnimeSeries.objects.filter(anime=self.anime).aggregate(largest=models.Max('row'))['largest']
        Anime.objects.filter(pk=self.anime.pk).update(dubbed=largest)

    def __str__(self):
        if self.anime.type == 0:
            return '{} - {}'.format(self.anime,self.row)
        else:
            return str(self.anime)