# Generated by Django 3.2 on 2021-08-03 12:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bid', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='bid',
            name='photos',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bid.bidimages', verbose_name='Фотографии'),
        ),
    ]
