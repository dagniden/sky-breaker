from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
import markdown
import re
from .models import Article


class ArticleListView(ListView):
    """Список всех статей курса"""
    model = Article
    template_name = 'sleepy/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10


class ArticleDetailView(DetailView):
    """Детальный просмотр статьи с конвертацией Markdown в HTML"""
    model = Article
    template_name = 'sleepy/article_detail.html'
    context_object_name = 'article'

    def get_object(self):
        return get_object_or_404(Article, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()

        # Конвертируем Markdown в HTML
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'fenced_code'])
        html_content = md.convert(article.content)

        # Обрабатываем wiki-ссылки [[День N]]
        html_content = self.process_wiki_links(html_content)

        context['html_content'] = html_content

        # Получаем предыдущую и следующую статьи для навигации
        context['prev_article'] = Article.objects.filter(
            day_number=article.day_number - 1
        ).first()
        context['next_article'] = Article.objects.filter(
            day_number=article.day_number + 1
        ).first()

        return context

    def process_wiki_links(self, content):
        """Конвертирует wiki-ссылки [[День N]] в HTML ссылки"""
        def replace_link(match):
            link_text = match.group(1)
            # Пытаемся найти статью по названию
            if link_text.startswith('День '):
                try:
                    day_num = int(link_text.replace('День ', '').strip())
                    article = Article.objects.filter(day_number=day_num).first()
                    if article:
                        return f'<a href="{article.get_absolute_url()}">{link_text}</a>'
                except (ValueError, Article.DoesNotExist):
                    pass
            return link_text

        # Заменяем [[текст]] на ссылки
        pattern = r'\[\[([^\]]+)\]\]'
        return re.sub(pattern, replace_link, content)
