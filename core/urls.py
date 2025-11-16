# core/urls.py
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # Маршрут для главной страницы
    path("", views.main_feed_view, name="main_feed"),
    path('posts/', views.htmx_post_list_view, name='post_list'),
    path('create-post/', views.htmx_create_post_view, name='create_post'),

]
