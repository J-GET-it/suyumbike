from django.contrib import admin
from .models import Place, Category, User

# Register your models here.

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'rating', 'average_check', 'address', 'date_until']
    list_filter = ['category', 'rating', 'date_until']
    search_fields = ['name', 'description', 'address']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'description', 'address', 'photo')
        }),
        ('Финансы и рейтинг', {
            'fields': ('average_check', 'rating')
        }),
        ('Социальные сети', {
            'fields': ('map_link', 'vk_link', 'instagram_link', 'telegram_link', 'web_link'),
            'classes': ('collapse',)
        }),
        ('Дата показа', {
            'fields': ('date_until',)
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_category', 'order']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'created_at']
    search_fields = ['telegram_id']
