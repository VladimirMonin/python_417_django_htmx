# core/views.py
from django.shortcuts import render

# Полная имитация выгрузки из базы данных.
# Структура словарей сделана так, чтобы полностью соответствовать
# обращениям в шаблоне (post.image.url, post.tags.all).
MOCK_POSTS = [
    {
        "id": 1,
        "title": "Первый пост о котиках",
        "image": {"url": "https://placehold.co/600x400/ffc107/000000?text=Котик+1"},
        "tags": {"all": [{"name": "Милота"}, {"name": "Животные"}]},
    },
    {
        "id": 2,
        "title": "Bootstrap 5: что нового?",
        "image": {"url": "https://placehold.co/600x400/ffc107/000000?text=Bootstrap"},
        "tags": {"all": [{"name": "Frontend"}, {"name": "CSS"}]},
    },
    {
        "id": 3,
        "title": "Изучаем Django и HTMX",
        "image": {"url": "https://placehold.co/600x400/ffc107/000000?text=Django+HTMX"},
        "tags": {"all": [{"name": "Backend"}, {"name": "Python"}, {"name": "HTMX"}]},
    },
]


def main_feed_view(request):
    """
    Отображает главную страницу с лентой постов.
    """
    context = {
        "posts": MOCK_POSTS,
    }
    return render(request, "core/main.html", context)
