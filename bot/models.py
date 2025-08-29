from django.db import models

# Create your models here.

class Category(models.Model):
    parent_category = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='category',
        help_text="Если подкатегория - выберите основную категорию"
    )
    name = models.CharField(max_length=200, verbose_name="Название категории")
    description = models.CharField(max_length=200, verbose_name="Короткое описание категории", null=True, blank=True)
    order = models.IntegerField(verbose_name="Порядковый номер", null=True, blank=True)
    day_clicks = models.IntegerField(verbose_name="Количество кликов за день", null=True, blank=True, default=0)
    all_clicks = models.IntegerField(verbose_name="Количество кликов за все время", null=True, blank=True, default=0)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order',]
    
    def __str__(self):
        return f"{self.name}"


class Place(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )

    name = models.CharField(max_length=200, verbose_name="Название места")
    description = models.TextField(verbose_name="Описание")
    address = models.CharField(max_length=500, verbose_name="Адрес", null=True, blank=True)
    average_check = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Средний чек", null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="Рейтинг", null=True, blank=True)
    
    # Необязательные поля
    web_link = models.CharField(blank=True, null=True,max_length=500, verbose_name="Ссылка на сайт")
    map_link = models.CharField(blank=True, null=True,max_length=500,  verbose_name="Ссылка на Яндекс Картах")
    vk_link = models.CharField(blank=True, null=True,max_length=500,  verbose_name="Ссылка ВКонтакте")
    instagram_link = models.CharField(blank=True, null=True,max_length=500,  verbose_name="Ссылка в Instagram")
    telegram_link = models.CharField(blank=True, null=True,max_length=500,  verbose_name="Ссылка в Telegram")
    photo = models.ImageField(blank=True, null=True, upload_to="image/")
    date_until = models.DateField(null=True, blank=True, verbose_name="Показывать до (включительно)")
    
    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
        ordering = ['-rating', 'name']
    
    def __str__(self):
        return f"{self.name}"

    def get_text(self):
        text = f"{self.name}\n\n{self.description}\n\n"
        if self.address:
            text += f"📍 {self.address}\n"
        if self.average_check:
            text += f"💰 Средний чек: {self.average_check}\n"
        if self.rating:
            text += f"⭐️ Рейтинг: {self.rating}"
        return text


class User(models.Model):
    telegram_id = models.CharField(primary_key=True, max_length=32, verbose_name="Telegram ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.telegram_id
