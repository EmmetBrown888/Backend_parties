# Generated by Django 3.2 on 2021-08-03 12:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('room_chat', '0001_initial'),
        ('ad', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор предложения о голосовании'),
        ),
        migrations.AddField(
            model_name='vote',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_candidate', to=settings.AUTH_USER_MODEL, verbose_name='Кандидат'),
        ),
        migrations.AddField(
            model_name='vote',
            name='voted',
            field=models.ManyToManyField(blank=True, related_name='voted_users', to=settings.AUTH_USER_MODEL, verbose_name='Проголосовавшие пользователи'),
        ),
        migrations.AddField(
            model_name='room',
            name='ad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ad.ad', verbose_name='Объявление'),
        ),
        migrations.AddField(
            model_name='room',
            name='blocked_user',
            field=models.ManyToManyField(blank=True, related_name='blocked_user', to=settings.AUTH_USER_MODEL, verbose_name='Заблокированные пользователи'),
        ),
        migrations.AddField(
            model_name='room',
            name='invited',
            field=models.ManyToManyField(related_name='invited_user', to=settings.AUTH_USER_MODEL, verbose_name='Участники'),
        ),
        migrations.AddField(
            model_name='room',
            name='voting',
            field=models.ManyToManyField(blank=True, default=None, related_name='voting_user', to='room_chat.Vote'),
        ),
        migrations.AddField(
            model_name='chat',
            name='images',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='room_chat.imagemessage', verbose_name='Фотографии'),
        ),
        migrations.AddField(
            model_name='chat',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='room_chat.room', verbose_name='Комната чата'),
        ),
        migrations.AddField(
            model_name='chat',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
