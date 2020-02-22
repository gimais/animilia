# Generated by Django 2.1.1 on 2020-02-22 20:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Anime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='სახელი')),
                ('nameen', models.CharField(blank=True, max_length=100, unique=True, verbose_name='ინგლისურად')),
                ('namejp', models.CharField(blank=True, max_length=100, unique=True, verbose_name='იაპონურად')),
                ('nameru', models.CharField(blank=True, max_length=100, unique=True, verbose_name='რუსულად')),
                ('dubber', models.CharField(max_length=16, verbose_name='გამხმოვანებელი')),
                ('poster', models.ImageField(blank=True, max_length=50, upload_to='posters/', verbose_name='სურათი')),
                ('year', models.PositiveSmallIntegerField(verbose_name='გამოშვების წელი')),
                ('director', models.CharField(max_length=40, verbose_name='რეჟისორი')),
                ('studio', models.CharField(max_length=20, verbose_name='სტუდია')),
                ('age', models.PositiveSmallIntegerField(verbose_name='შეზღუდვის ასაკი')),
                ('description', models.TextField(verbose_name='აღწერა')),
                ('type', models.PositiveSmallIntegerField(choices=[(0, 'სერიალი'), (1, 'კინო')], default=0, verbose_name='ტიპი')),
                ('episodes', models.PositiveSmallIntegerField(default=1, verbose_name='ეპიზოდების რაოდენობა')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(unique=True, verbose_name='ლინკი')),
            ],
            options={
                'verbose_name': 'Anime',
                'verbose_name_plural': 'Anime',
                'db_table': 'animes_list',
            },
        ),
        migrations.CreateModel(
            name='AnimeSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=60, verbose_name='ვიდეოს ლინკი')),
                ('row', models.PositiveSmallIntegerField(default=1, verbose_name='მერამდენე ეპიზოდია')),
                ('anime', models.ForeignKey(limit_choices_to={'type': 0}, on_delete=django.db.models.deletion.CASCADE, to='anime.Anime', verbose_name='ანიმე')),
            ],
            options={
                'verbose_name': 'Anime Serie',
                'verbose_name_plural': 'Anime Series',
                'db_table': 'animes_series',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('name', models.CharField(max_length=18, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'db_table': 'categories',
            },
        ),
        migrations.AddField(
            model_name='anime',
            name='categories',
            field=models.ManyToManyField(related_name='categories', to='anime.Category', verbose_name='ჟანრები'),
        ),
    ]
