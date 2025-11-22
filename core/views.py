# core/views.py
from time import sleep
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.core.paginator import Paginator
from django.db.models import F
from .forms import PostForm
from .models import Post
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods

# Константа для количества постов на страницу
POSTS_PER_PAGE = 5


def main_feed_view(request):
    """
    Отображает главную страницу с лентой постов.
    Поддерживает пагинацию через GET параметр 'page'.
    """
    posts = (
        Post.objects.select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at")
    )

    # Пагинация с поддержкой GET параметра
    page = request.GET.get("page", 1)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(page)

    context = {
        "posts": page_obj,
        "page_obj": page_obj,
        "form": PostForm(),
    }
    return render(request, "core/main.html", context)


def htmx_post_list_view(request):
    """
    Возвращает только HTML-фрагмент со списком постов.
    Поддерживает пагинацию для бесконечной прокрутки.
    """
    sleep(2)
    posts = (
        Post.objects.select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at")
    )

    # Пагинация
    page = request.GET.get("page", 1)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(page)

    context = {
        "posts": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "core/_posts_list.html", context)


def htmx_create_post_view(request):
    """
    Обрабатывает POST-запрос от HTMX для создания нового поста.
    """
    sleep(5)
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save()
        # Возвращаем HTML-фрагмент только что созданной карточки
        return render(request, "core/_card.html", {"post": post})
    else:
        # Если форма невалидна, возвращаем форму с ошибками
        return render(request, "core/_post_form.html", {"form": form})


@staff_member_required
@require_http_methods(["DELETE"])
def htmx_delete_post_view(request, post_id):
    """
    Удаляет пост. Доступно только для персонала сайта.
    """
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return HttpResponse("", status=200)


@require_http_methods(["POST"])
def htmx_like_post_view(request, post_id):
    """
    Обрабатывает лайк поста с учетом сессии.
    Реализует логику "или/или" и отмену лайка.
    """
    post = get_object_or_404(Post, id=post_id)

    # Получаем списки из сессии, если их нет - создаем пустые
    liked_posts = request.session.get("liked_posts", [])
    disliked_posts = request.session.get("disliked_posts", [])

    # Если пост уже был лайкнут - снимаем лайк (toggle)
    if post_id in liked_posts:
        post.likes = F("likes") - 1
        liked_posts.remove(post_id)
    else:
        # Если пост не был лайкнут - ставим лайк
        post.likes = F("likes") + 1
        liked_posts.append(post_id)
        # И если он был дизлайкнут - снимаем дизлайк
        if post_id in disliked_posts:
            post.dislikes = F("dislikes") - 1
            disliked_posts.remove(post_id)

    post.save()
    post.refresh_from_db()  # Обновляем объект для корректного отображения
    request.session["liked_posts"] = liked_posts
    request.session["disliked_posts"] = disliked_posts

    return render(request, "core/_card.html", {"post": post})


@require_http_methods(["POST"])
def htmx_dislike_post_view(request, post_id):
    """
    Обрабатывает дизлайк поста с учетом сессии.
    Реализует логику "или/или" и отмену дизлайка.
    """
    post = get_object_or_404(Post, id=post_id)

    liked_posts = request.session.get("liked_posts", [])
    disliked_posts = request.session.get("disliked_posts", [])

    # Если пост уже был дизлайкнут - снимаем дизлайк
    if post_id in disliked_posts:
        post.dislikes = F("dislikes") - 1
        disliked_posts.remove(post_id)
    else:
        # Если не был - ставим дизлайк
        post.dislikes = F("dislikes") + 1
        disliked_posts.append(post_id)
        # И если он был лайкнут - снимаем лайк
        if post_id in liked_posts:
            post.likes = F("likes") - 1
            liked_posts.remove(post_id)

    post.save()
    post.refresh_from_db()  # Обновляем объект для корректного отображения
    request.session["liked_posts"] = liked_posts
    request.session["disliked_posts"] = disliked_posts

    return render(request, "core/_card.html", {"post": post})


@staff_member_required
@require_http_methods(["GET", "POST"])
def htmx_edit_post_view(request, post_id):
    """
    Редактирует пост. Доступно только для персонала сайта.
    GET: возвращает форму редактирования
    POST: сохраняет изменения и возвращает обновленную карточку
    """
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            return render(request, "core/_card.html", {"post": post})
        else:
            return render(
                request, "core/_post_edit_form.html", {"form": form, "post": post}
            )

    # GET запрос - возвращаем форму редактирования
    form = PostForm(instance=post)
    return render(request, "core/_post_edit_form.html", {"form": form, "post": post})
