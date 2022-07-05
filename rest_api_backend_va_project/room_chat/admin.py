from django.contrib import admin

from .models import Room, Vote, Chat, ImageMessage


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Chat rooms"""
    list_display = ('ad',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Ad"""
    list_display = ('author', 'candidate', 'votes')


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """Dialogs"""
    list_display = ('room', 'user', 'text', 'date')


@admin.register(ImageMessage)
class ImageMessageAdmin(admin.ModelAdmin):
    """Images"""
    list_display = ('first_image', 'second_image', 'date')
