# core/urls.py
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # Маршрут для главной страницы
    path("", views.main_feed_view, name="main_feed"),
    path('posts/', views.htmx_post_list_view, name='post_list'),
    path('create-post/', views.htmx_create_post_view, name='create_post'),
    path('delete-post/<int:post_id>/', views.htmx_delete_post_view, name='delete_post'),
    path('like-post/<int:post_id>/', views.htmx_like_post_view, name='like_post'),
    path('dislike-post/<int:post_id>/', views.htmx_dislike_post_view, name='dislike_post'),
    path('edit-post/<int:post_id>/', views.htmx_edit_post_view, name='edit_post'),
]
