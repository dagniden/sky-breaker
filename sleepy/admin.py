from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('day_number', 'title', 'slug', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('day_number',)
