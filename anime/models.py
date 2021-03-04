from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import F
from django.utils.functional import cached_property


class Category(models.Model):
    name = models.CharField(max_length=18, unique=True, verbose_name='სახელი')

    class Meta:
        db_table = 'category'
        verbose_name = 'კატეგორია'
        verbose_name_plural = 'კატეგორია'

    def __str__(self):
        return self.name


class Dubber(models.Model):
    name = models.CharField(max_length=16, unique=True, verbose_name='სახელი')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'dubber'
        verbose_name = 'გამხმოვანებელი'
        verbose_name_plural = 'გამხმოვანებელი'

    def __str__(self):
        return self.name

    @cached_property
    def get_dubbed_animes(self):
        return self.dubbed.all()


class WatchingOrderingGroup(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='ჯგუფის სახელი')

    class Meta:
        verbose_name = "ყურების განრიგი"
        verbose_name_plural = "ყურების განრიგი"
        db_table = "anime_ordering"

    def __str__(self):
        return self.name


class WatchOrder(models.Model):
    anime = models.OneToOneField("Anime", null=True, blank=True,
                                 related_name='animeorder', verbose_name='ანიმე', on_delete=models.CASCADE)
    not_here = models.CharField(max_length=100, null=True, blank=True, verbose_name='სხვა',
                                help_text="თუ ანიმეს სიაში არ არის ესეიგი ჩვენთან ბაზაში არაა და ხელით აქ ჩაწერე")
    ordering_group = models.ForeignKey(WatchingOrderingGroup, default=None,
                                       related_name='ordergroup', verbose_name='ჯგუფი', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "მიმდევრობა"
        verbose_name_plural = "მიმდევრობა"

    def __str__(self):
        return self.anime.name if self.anime is not None else self.not_here


class Anime(models.Model):
    TYPES = (
        (0, 'სერიალი'),
        (1, 'ფილმი'),
        (2, 'OVA'),
        (3, 'ONA'),
        (4, 'ანიმაციური ფილმი'),
    )

    name = models.CharField(max_length=100, verbose_name='სახელი', unique=True)
    namege = models.CharField(max_length=100, verbose_name='ქართულად', blank=True)
    nameen = models.CharField(max_length=100, verbose_name='ინგლისურად', blank=True)
    namejp = models.CharField(max_length=100, verbose_name='იაპონურად', blank=True)
    nameru = models.CharField(max_length=100, verbose_name='რუსულად', blank=True)
    dubbers = models.ManyToManyField(Dubber, related_name='dubbed', verbose_name='გამხმოვანებელი')
    poster = models.ImageField(upload_to='posters/', max_length=50, blank=True, verbose_name='სურათი')
    year = models.PositiveSmallIntegerField(verbose_name='გამოშვების წელი')
    director = models.CharField(max_length=45, verbose_name='რეჟისორი')
    studio = models.CharField(max_length=45, verbose_name='სტუდია')
    age = models.PositiveSmallIntegerField(verbose_name='შეზღუდვის ასაკი')
    description = models.TextField(verbose_name='აღწერა')
    categories = models.ManyToManyField(Category, related_name='categories', verbose_name='ჟანრები')
    type = models.PositiveSmallIntegerField(choices=TYPES, default=0, verbose_name='ტიპი')
    episodes = models.PositiveSmallIntegerField(verbose_name='ეპიზოდების რაოდენობა', default=1)
    rating = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='რეიტინგი')
    updated = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0, editable=False)
    dubbed = models.PositiveSmallIntegerField(default=0, verbose_name='გახმოვანებული', editable=False)
    slug = models.SlugField(unique=True, verbose_name='ლინკი')
    finished = models.BooleanField(default=False, verbose_name="დამთავრებულია")
    soon = models.BooleanField(default=False, verbose_name="მალე")

    class Meta:
        permissions = [
            ("view_all_anime", "ყველა ანიმეს ნახვის უფლება"),
        ]

        db_table = 'anime'
        verbose_name = 'ანიმე'
        verbose_name_plural = 'ანიმე'

    def increase_view_count(self, cookies):
        if not cookies.get('_vEpAd', False):
            Anime.objects.filter(pk=self.pk).update(views=F('views') + 1)

    def save(self, *args, **kwargs):
        if self.type == 1:
            self.episodes = 1

        super(Anime, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/anime/{self.slug}'

    def __str__(self):
        return self.name


class Video(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, limit_choices_to={'type': 0}, related_name='videos')
    url = models.CharField(max_length=100, verbose_name='ვიდეოს ლინკი')
    row = models.PositiveSmallIntegerField(default=1, verbose_name='ეპიზოდი', editable=False)

    class Meta:
        db_table = 'anime_video'
        verbose_name = 'ვიდეო'
        verbose_name_plural = 'ვიდეოები'

    def delete(self, using=None, keep_parents=False):
        super(Video, self).delete()

        largest = Video.objects.filter(anime=self.anime).aggregate(largest=models.Max('row'))['largest']
        Anime.objects.filter(pk=self.anime.pk).update(dubbed=largest)

    def save(self, *args, **kwargs):
        # Todo Optimize
        if self._state.adding:
            last_id = Video.objects.filter(anime=self.anime).aggregate(largest=models.Max('row'))['largest']

            if self.anime.type == 1 and last_id is not None:
                return

            if last_id is not None:
                self.row = last_id + 1

        super(Video, self).save(*args, **kwargs)

        Anime.objects.get(pk=self.anime.pk).updated = datetime.now()  # update after adding episodes

        Anime.save(self.anime)

        largest = Video.objects.filter(anime=self.anime).aggregate(largest=models.Max('row'))['largest']
        Anime.objects.filter(pk=self.anime.pk).update(dubbed=largest)

    def __str__(self):
        if self.anime.type == 0:
            return '{} - {}'.format(self.anime, self.row)
        else:
            return str(self.anime)


class Schedule(models.Model):
    anime = models.OneToOneField(Anime, on_delete=models.CASCADE, related_name='schedule', verbose_name='ანიმე',
                                 error_messages={'unique': 'განრიგი ამ ანიმეზე უკვე არსებობს'})
    date = models.DateField(verbose_name='თარიღი')
    from_time = models.TimeField(verbose_name='დან')
    to_time = models.TimeField(verbose_name='მდე')
    text = models.TextField(max_length=400, blank=True, verbose_name='ტექსტი',
                            help_text="თუ ეს ტექსტი ცარიელი იქნება, მაშინ საიტზე მხოლოდ თარიღი გამოჩნდება,"
                                      " წინააღმდეგ შემთხვევაში მხოლოდ ტექსტი გამოჩდნება")

    class Meta:
        permissions = [
            ("view_all_schedule", "ყველა განრიგის ნახვის უფლება"),
        ]

        db_table = 'schedule'
        verbose_name = 'განრიგი'
        verbose_name_plural = 'განრიგი'

    def __str__(self):
        return str(self.anime)
