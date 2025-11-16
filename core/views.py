# core/views.py
from django.shortcuts import render
from .forms import PostForm

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
        "form": PostForm(),
    }
    return render(request, "core/main.html", context)


def post_list_view(request):
    """
    Возвращает только HTML-фрагмент со списком постов.
    """
    context = {"posts": MOCK_POSTS}
    # Обратите внимание: рендерим не 'main.html', а только 'партиал'
    return render(request, "core/_posts_list.html", context)


def create_post_view(request):
    """
    Обрабатывает POST-запрос от HTMX для создания нового поста.
    """
    from time import sleep

    sleep(5)
    form = PostForm(request.POST, request.FILES)

    if form.is_valid():
        post = form.save()
        # Возвращаем HTML-фрагмент только что созданной карточки
        return render(request, "core/_card.html", {"post": post})

    else:
        # Если форма невалидна, возвращаем форму с ошибками
        return render(request, "core/_create_post_form.html", {"form": form})
