from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Participant, ParticipantImages


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("user", "ad", "number_of_person", "number_of_girls", "number_of_boys", "create_ad")
    list_filter = ("ad__city", "create_ad")


class ParticipantImagesAdmin(admin.ModelAdmin):
    list_display = ("photo_participants", "get_photo_participants", "photo_alcohol", "get_photo_alcohol")

    def get_photo_participants(self, obj):
        if obj.photo_participants:
            return mark_safe(f'<img src={obj.photo_participants.url} width="200" height="200"')
        else:
            return mark_safe(f'<img src="" alt="" width="100" height="100"')

    get_photo_participants.short_description = "Изображение"

    def get_photo_alcohol(self, obj):
        if obj.photo_alcohol:
            return mark_safe(f'<img src={obj.photo_alcohol.url} width="200" height="200"')
        else:
            return mark_safe(f'<img src="" alt="" width="100" height="100"')

    get_photo_alcohol.short_description = "Изображение"


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(ParticipantImages, ParticipantImagesAdmin)
