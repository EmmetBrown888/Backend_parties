from django.contrib import admin

from .models import Ad


def make_published(modeladmin, request, queryset):
    queryset.update(is_published=True)


make_published.short_description = "Опубликовать выбранные Объявления"


class AdAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'city', 'number_of_person', 'number_of_girls',
        'number_of_boys', 'party_date', 'is_published', 'create_ad'
    )
    list_filter = ('city', 'party_date', 'is_published')

    readonly_fields = (
        'title', 'author', 'city', 'number_of_person', 'number_of_girls',
        'number_of_boys', 'party_date', 'geolocation', 'participants', 'create_ad'
    )

    actions = (make_published,)


admin.site.register(Ad, AdAdmin)
