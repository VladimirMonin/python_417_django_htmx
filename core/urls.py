# core/urls.py
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # Маршрут для главной страницы
    path("", views.main_feed_view, name="main_feed"),
]
