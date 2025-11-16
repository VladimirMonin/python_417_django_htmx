# core/forms.py
from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # Указываем, какие поля из модели должны быть в форме
        fields = ["title", "image", "tags", "content", "category"]
        # Можно добавить виджеты для кастомизации полей
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
            "content": forms.Textarea(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }
