import os
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from sleepy.models import Article


class Command(BaseCommand):
    help = 'Импорт статей из Markdown файлов в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default='data/Sleepy',
            help='Путь к директории с Markdown файлами'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить базу данных перед импортом'
        )

    def handle(self, *args, **options):
        data_path = Path(options['path'])

        if not data_path.exists():
            self.stdout.write(self.style.ERROR(f'Директория {data_path} не найдена'))
            return

        if options['clear']:
            Article.objects.all().delete()
            self.stdout.write(self.style.WARNING('База данных очищена'))

        # Получаем все MD файлы кроме плана курса
        md_files = [f for f in data_path.glob('День *.md')]

        if not md_files:
            self.stdout.write(self.style.ERROR('Не найдено файлов формата "День N.md"'))
            return

        imported_count = 0
        updated_count = 0
        error_count = 0

        for md_file in sorted(md_files):
            try:
                # Извлекаем номер дня из имени файла
                day_match = re.search(r'День (\d+)', md_file.name)
                if not day_match:
                    self.stdout.write(self.style.WARNING(f'Пропущен файл {md_file.name}: не найден номер дня'))
                    continue

                day_number = int(day_match.group(1))

                # Читаем содержимое файла
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Извлекаем теги
                tags = self.extract_tags(content)

                # Извлекаем заголовок (первый текстовый тег после #Sleepy/)
                title = self.extract_title(content, tags, day_number)

                # Генерируем slug
                slug = slugify(f'den-{day_number}-{title}', allow_unicode=False)

                # Создаем или обновляем статью
                article, created = Article.objects.update_or_create(
                    day_number=day_number,
                    defaults={
                        'title': title,
                        'slug': slug,
                        'content': content,
                        'tags': tags,
                    }
                )

                if created:
                    imported_count += 1
                    self.stdout.write(self.style.SUCCESS(f'[+] Импортирована: День {day_number} - {title}'))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'[*] Обновлена: День {day_number} - {title}'))

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'[!] Ошибка при импорте {md_file.name}: {str(e)}'))

        # Итоговая статистика
        self.stdout.write(self.style.SUCCESS(f'\n{"="*50}'))
        self.stdout.write(self.style.SUCCESS(f'Импорт завершен:'))
        self.stdout.write(self.style.SUCCESS(f'  Создано новых: {imported_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Обновлено: {updated_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'  Ошибок: {error_count}'))
        self.stdout.write(self.style.SUCCESS(f'{"="*50}'))

    def extract_tags(self, content):
        """Извлекает теги из формата #Sleepy/Тег"""
        tag_pattern = r'#Sleepy/([^\s\n]+)'
        tags = re.findall(tag_pattern, content)
        # Заменяем дефисы и подчеркивания на пробелы для читаемости
        tags = [tag.replace('_', ' ').replace('-', ' ') for tag in tags]
        return ', '.join(tags) if tags else ''

    def extract_title(self, content, tags, day_number):
        """Извлекает заголовок статьи"""
        # Пробуем взять первый тег как заголовок
        if tags:
            # Берем первый тег до запятой
            first_tag = tags.split(',')[0].strip()
            return first_tag

        # Если нет тегов, пробуем найти первый заголовок в markdown
        title_match = re.search(r'^#+\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()

        # Если ничего не нашли, используем номер дня
        return f'День {day_number}'
