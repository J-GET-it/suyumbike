from django.contrib import admin
from .models import Place, Category

# Register your models here.

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'rating', 'average_check', 'address']
    list_filter = ['category', 'rating']
    search_fields = ['name', 'description', 'address']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'description', 'address')
        }),
        ('Финансы и рейтинг', {
            'fields': ('average_check', 'rating')
        }),
        ('Социальные сети', {
            'fields': ('vk_link', 'instagram_link', 'telegram_link'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'classes': ('collapse',)
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']