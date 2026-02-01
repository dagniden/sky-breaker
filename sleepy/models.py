from django.db import models
from django.urls import reverse


class Article(models.Model):
    """Статья курса Sleepy"""

    day_number = models.IntegerField(
        unique=True,
        verbose_name="День курса",
        help_text="Номер дня (1-30)"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="URL slug"
    )
    content = models.TextField(
        verbose_name="Контент (Markdown)"
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Теги"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['day_number']

    def __str__(self):
        return f"День {self.day_number}: {self.title}"

    def get_absolute_url(self):
        return reverse('sleepy:article_detail', kwargs={'slug': self.slug})
