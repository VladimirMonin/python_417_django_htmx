# core/views.py
from django.shortcuts import render, get_object_or_404, HttpResponse
from .forms import PostForm
from .models import Post
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods


def main_feed_view(request):
    """
    Отображает главную страницу с лентой постов.
    """
    from django.core.paginator import Paginator
    
    posts = (
        Post.objects.select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    
    # Пагинация для начальной загрузки
    paginator = Paginator(posts, 5)  # 5 постов на страницу
    page_obj = paginator.get_page(1)
    
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
    from time import sleep
    from django.core.paginator import Paginator

    sleep(2)
    posts = (
        Post.objects.select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    
    # Пагинация
    page = request.GET.get('page', 1)
    paginator = Paginator(posts, 5)  # 5 постов на страницу
    posts_page = paginator.get_page(page)
    
    context = {
        "posts": posts_page,
        "page_obj": posts_page,
    }
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
    Увеличивает счетчик лайков поста.
    """
    post = get_object_or_404(Post, id=post_id)
    post.likes += 1
    post.save()
    return render(request, "core/_card.html", {"post": post})


@require_http_methods(["POST"])
def htmx_dislike_post_view(request, post_id):
    """
    Увеличивает счетчик дизлайков поста.
    """
    post = get_object_or_404(Post, id=post_id)
    post.dislikes += 1
    post.save()
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
            return render(request, "core/_post_edit_form.html", {"form": form, "post": post})
    
    # GET запрос - возвращаем форму редактирования
    form = PostForm(instance=post)
    return render(request, "core/_post_edit_form.html", {"form": form, "post": post})
