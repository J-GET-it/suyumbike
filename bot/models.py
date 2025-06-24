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

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    
    def __str__(self):
        return f"{self.name}"

    def has_children(self):
        if self.parent_category is None:
            return False
        return True

class Place(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )

    name = models.CharField(max_length=200, verbose_name="Название места")
    description = models.TextField(verbose_name="Описание")
    address = models.CharField(max_length=500, verbose_name="Адрес")
    average_check = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Средний чек")
    rating = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="Рейтинг")
    
    # Необязательные поля
    vk_link = models.URLField(blank=True, null=True, verbose_name="Ссылка ВКонтакте")
    instagram_link = models.URLField(blank=True, null=True, verbose_name="Ссылка в Instagram")
    telegram_link = models.URLField(blank=True, null=True, verbose_name="Ссылка в Telegram")
    photo = models.ImageField(blank=True, null=True, upload_to="image/")
    
    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
        ordering = ['-rating', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def get_text(self):
        return f"Сегодня в {self.name}\n\n{self.description}\n\n📍 {self.address}\n💰 Средний чек: {self.average_check}\n⭐️ Рейтинг: {self.rating}"
