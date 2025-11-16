# core/views.py
from django.shortcuts import render
from .forms import PostForm
from .models import Post


def main_feed_view(request):
    """
    Отображает главную страницу с лентой постов.
    """
    posts = (
        Post.objects.select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    context = {
        "posts": posts,
        "form": PostForm(),
    }
    return render(request, "core/main.html", context)


def htmx_post_list_view(request):
    """
    Возвращает только HTML-фрагмент со списком постов.
    """
    posts = (
        Post.objects.select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    context = {"posts": posts}
    return render(request, "core/_posts_list.html", context)


def htmx_create_post_view(request):
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
        return render(request, "core/_post_form.html", {"form": form})
