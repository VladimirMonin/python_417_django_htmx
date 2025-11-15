# core/models.py
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name="Название категории"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Название тега")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    # Картинки будут загружаться в папку 'uploads/posts/' внутри вашего MEDIA_ROOT
    image = models.ImageField(upload_to="posts/", verbose_name="Изображение")

    # Связь с категорией: один пост -> одна категория
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Категория",
    )

    # Связь с тегами: один пост -> много тегов
    tags = models.ManyToManyField(
        Tag, blank=True, related_name="posts", verbose_name="Теги"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
