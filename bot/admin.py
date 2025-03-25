from django.contrib import admin
from bot.models import User, Presentations


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_admin')
    search_fields = ('user_id', 'is_admin')
    list_filter = ('is_admin', 'username')


class PresentationsAdmin(admin.ModelAdmin):
    list_display = ('user', 'adress')  # Поля для отображения в админке


admin.site.register(User, UserAdmin)
admin.site.register(Presentations, PresentationsAdmin)  # Регистрация модели Goods с админкой
