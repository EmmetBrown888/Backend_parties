from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import User, Subscription


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "email", "get_image", "date_joined")
    list_filter = ("date_joined", "is_superuser")

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return [
                "username", "first_name", "last_name", "email", "get_image", "date_joined", 
                "is_staff", "is_active", "city", "birth_day", "sex", "code_confirm", "photo",
                "subscription", "is_superuser", "groups", "user_permissions", "password", "last_login"
            ]

    def get_image(self, obj):
        if obj.photo:
            return mark_safe(f'<img src={obj.photo.url} width="100" height="110"')
        else:
            return mark_safe(f'<img src="" alt="" width="100" height="110"')

    get_image.short_description = "Изображение"


admin.site.site_header = "Административная панель VA"
admin.site.index_title = "Модели"
admin.site.register(User, UserAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Subscription, SubscriptionAdmin)
