# Как работает пагинация с HTMX - объяснение для людей

## 🎯 Что мы хотим получить?

Кликаем "Показать больше" → посты добавляются внизу → кнопка обновляется (показывает следующую страницу)

---

## 📦 Что у нас есть (файлы)

```
core/
├── views.py
│   ├── main_feed_view()         # Первая загрузка страницы
│   └── htmx_post_list_view()    # HTMX запрос за новыми постами
│
└── templates/core/
    ├── main.html                # Полная страница
    ├── _posts_list.html         # Фрагмент: посты + пагинатор (для HTMX)
    ├── _card.html               # Одна карточка поста
    └── _paginator.html          # Кнопка + номера страниц
```

---

## 🚀 СЦЕНАРИЙ 1: Первая загрузка (без HTMX)

### Шаг 1: Пользователь открывает сайт

```
Браузер → GET / → Django
```

### Шаг 2: Django вызывает `main_feed_view`

```python
def main_feed_view(request):
    # Берём все посты
    posts = Post.objects.all().order_by("-created_at")
    
    # Делим на страницы по 5 штук
    paginator = Paginator(posts, 5)
    
    # Берём страницу 1 (или из GET параметра ?page=2)
    page = request.GET.get("page", 1)
    page_obj = paginator.get_page(page)
    
    # Отдаём ПОЛНУЮ страницу
    return render(request, "core/main.html", {
        "posts": page_obj,      # 5 постов
        "page_obj": page_obj,   # Инфа о странице
    })
```

### Шаг 3: Рендерится `main.html`

```html
<!-- main.html -->
<div id="posts-list">
    <!-- Цикл выводит 5 постов -->
    <div class="card post-card">Пост 1</div>
    <div class="card post-card">Пост 2</div>
    <div class="card post-card">Пост 3</div>
    <div class="card post-card">Пост 4</div>
    <div class="card post-card">Пост 5</div>
</div>

<!-- Пагинатор -->
<div id="pagination-controls">
    <button hx-get="/posts/?page=2">Показать больше</button>
    <nav>[1] 2 3</nav>
</div>
```

**Что видит пользователь:**

- 5 постов
- Жёлтая кнопка "Показать больше"
- Номера: [1] 2 3 (первая активна)

---

## 🔥 СЦЕНАРИЙ 2: Клик "Показать больше" (с HTMX)

### Шаг 1: Пользователь кликает кнопку

```html
<button 
    hx-get="/posts/?page=2"      <!-- Куда стучимся -->
    hx-target="#posts-list"       <!-- Куда вставлять -->
    hx-swap="beforeend"           <!-- Вставить В КОНЕЦ -->
    hx-select=".post-card"        <!-- Взять только карточки -->
>
    Показать больше
</button>
```

**HTMX делает:**

```javascript
// Примерно так (но вы не пишете этот код!)
fetch('/posts/?page=2', {
    headers: { 'HX-Request': 'true' }
})
.then(response => response.text())
.then(html => {
    // Парсит HTML, выбирает .post-card
    // Вставляет в конец #posts-list
})
```

### Шаг 2: Django получает запрос

```
HTMX → GET /posts/?page=2 → Django → htmx_post_list_view()
```

**Важно!** Django вызывает ДРУГУЮ функцию (не `main_feed_view`), потому что URL `/posts/` указан в `urls.py`:

```python
# urls.py
urlpatterns = [
    path("", views.main_feed_view, name="main_feed"),           # Полная страница
    path("posts/", views.htmx_post_list_view, name="post_list"), # HTMX фрагмент
]
```

### Шаг 3: Django рендерит `_posts_list.html`

```python
def htmx_post_list_view(request):
    posts = Post.objects.all().order_by("-created_at")
    
    # Теперь берём страницу 2!
    page = request.GET.get("page", 1)  # page = "2"
    paginator = Paginator(posts, 5)
    page_obj = paginator.get_page(page)  # Посты 6-10
    
    # ❗ page_obj содержит инфу о пагинации:
    # page_obj.number = 2 (текущая страница)
    # page_obj.next_page_number = 3 (следующая!)
    # page_obj.has_next = True
    
    # Возвращаем ФРАГМЕНТ (не полную страницу!)
    return render(request, "core/_posts_list.html", {
        "posts": page_obj,
        "page_obj": page_obj,  # ← Это Django передаёт в шаблон!
    })
```

**Django рендерит шаблон `_posts_list.html`:**

```django
<!-- _posts_list.html -->

<!-- Цикл генерирует 5 карточек -->
{% for post in posts %}
    <div class="card post-card">{{ post.title }}</div>
{% endfor %}

<!-- Шаблон _paginator.html -->
{% include 'core/_paginator.html' %}
```

**Django рендерит шаблон `_paginator.html`:**

```django
<div id="pagination-controls" hx-swap-oob="true">
    {% if page_obj.has_next %}
    <button hx-get="/posts/?page={{ page_obj.next_page_number }}">
        Показать больше
    </button>
    {% endif %}
    
    <nav>
        {% for num in page_obj.paginator.page_range %}
            {% if page_obj.number == num %}[{{ num }}]{% else %}{{ num }}{% endif %}
        {% endfor %}
    </nav>
</div>
```

**Django ВЫЧИСЛЯЕТ значения:**

- `page_obj.has_next` = True (есть страница 3)
- `page_obj.next_page_number` = 3 (2 + 1)
- `page_obj.number` = 2 (текущая)
- `page_obj.paginator.page_range` = [1, 2, 3]

**Django ГЕНЕРИРУЕТ финальный HTML:**

```html
<!-- Это Django отправит браузеру! -->

<!-- 5 новых постов -->
<div class="card post-card">Пост 6</div>
<div class="card post-card">Пост 7</div>
<div class="card post-card">Пост 8</div>
<div class="card post-card">Пост 9</div>
<div class="card post-card">Пост 10</div>

<!-- Пагинатор (Django ПОДСТАВИЛ page=3!) -->
<div id="pagination-controls" hx-swap-oob="true">
    <button hx-get="/posts/?page=3">Показать больше</button>
    <nav>1 [2] 3</nav>
</div>
```

**❗ ВАЖНО:** Номер страницы `3` генерирует **DJANGO**, а не HTMX!  
HTMX просто вставляет готовый HTML от сервера!

### Шаг 4: HTMX обрабатывает ответ ОТ СЕРВЕРА

**БРАУЗЕР получает HTTP ответ от Django (обычный HTML текст):**

```html
<div class="card post-card">Пост 6</div>
<div class="card post-card">Пост 7</div>
<div class="card post-card">Пост 8</div>
<div class="card post-card">Пост 9</div>
<div class="card post-card">Пост 10</div>
<div id="pagination-controls" hx-swap-oob="true">
    <button hx-get="/posts/?page=3">Показать больше</button>
    <nav>1 [2] 3</nav>
</div>
```

**HTMX (JavaScript в браузере) парсит этот HTML и делает ДВА действия:**

---

#### Действие А: Вставить карточки

**HTMX читает атрибуты кнопки (которую кликнули):**

```html
hx-select=".post-card"   ← Взять только элементы с классом .post-card
hx-target="#posts-list"  ← Вставить в элемент #posts-list
hx-swap="beforeend"      ← Вставить В КОНЕЦ (не заменять!)
```

**HTMX выполняет:**

```
1. Парсит HTML от сервера
2. Находит все элементы с классом .post-card:
   - <div class="card post-card">Пост 6</div>
   - <div class="card post-card">Пост 7</div>
   - <div class="card post-card">Пост 8</div>
   - <div class="card post-card">Пост 9</div>
   - <div class="card post-card">Пост 10</div>

3. Ищет на СТРАНИЦЕ элемент #posts-list

4. Вставляет карточки В КОНЕЦ этого элемента
```

**❓ ЗАЧЕМ `hx-select=".post-card"`?**

**Без него:** HTMX вставил бы ВСЁ, включая пагинатор → получился бы вложенный пагинатор!

**С ним:** HTMX берёт ТОЛЬКО карточки, игнорирует пагинатор (он обновится через OOB)

**Было:**

```html
<div id="posts-list">
    <div class="card post-card">Пост 1</div>
    <div class="card post-card">Пост 2</div>
    <div class="card post-card">Пост 3</div>
    <div class="card post-card">Пост 4</div>
    <div class="card post-card">Пост 5</div>
</div>
```

**Стало:**

```html
<div id="posts-list">
    <div class="card post-card">Пост 1</div>
    <div class="card post-card">Пост 2</div>
    <div class="card post-card">Пост 3</div>
    <div class="card post-card">Пост 4</div>
    <div class="card post-card">Пост 5</div>
    <!-- ↓ ДОБАВИЛИСЬ ↓ -->
    <div class="card post-card">Пост 6</div>
    <div class="card post-card">Пост 7</div>
    <div class="card post-card">Пост 8</div>
    <div class="card post-card">Пост 9</div>
    <div class="card post-card">Пост 10</div>
</div>
```

#### Действие Б: Заменить пагинатор

**HTMX видит в ответе ОТ СЕРВЕРА:**

```html
<div id="pagination-controls" hx-swap-oob="true">
    <button hx-get="/posts/?page=3">Показать больше</button>
    <nav>1 [2] 3</nav>
</div>
```

**HTMX думает:**
> "У этого элемента есть `hx-swap-oob="true"` и `id="pagination-controls"`  
> Значит надо найти НА СТРАНИЦЕ элемент с таким же id и ЗАМЕНИТЬ его на ТОТ, ЧТО ПРИШЁЛ ОТ СЕРВЕРА!"

**❓ ОТКУДА HTMX ЗНАЕТ ПРО `page=3`?**

**Ответ: НЕ ЗНАЕТ! Это DJANGO СГЕНЕРИРОВАЛ в шаблоне!**

Когда Django рендерил `_paginator.html`, он делал:

```django
<button hx-get="/posts/?page={{ page_obj.next_page_number }}">
```

Django **ПОДСТАВИЛ** `next_page_number`:

- Мы запросили `page=2`
- Django вычислил: следующая = 2 + 1 = 3
- Django **ВСТАВИЛ** в HTML: `page=3`

**HTMX просто ТУПО ЗАМЕНЯЕТ HTML**, не думая про номера страниц!

---

**Было на странице (ДО замены):**

```html
<div id="pagination-controls">
    <button hx-get="/posts/?page=2">Показать больше</button>
    <nav>[1] 2 3</nav>
</div>
```

**Пришло от сервера (Django сгенерировал):**

```html
<div id="pagination-controls" hx-swap-oob="true">
    <button hx-get="/posts/?page=3">Показать больше</button>
    <nav>1 [2] 3</nav>
</div>
```

**Стало на странице (ПОСЛЕ замены):**

```html
<div id="pagination-controls">
    <button hx-get="/posts/?page=3">Показать больше</button>
    <nav>1 [2] 3</nav>
</div>
```

**HTMX просто взял HTML от сервера и вставил!**

---

## 🔑 Ключевой момент: `hx-swap-oob`

### Зачем он нужен?

**Без `hx-swap-oob`:**

```
hx-target="#posts-list" → Вставляются только посты
                        → Пагинатор НЕ ОБНОВЛЯЕТСЯ
                        → Кнопка всегда показывает page=2
                        → При повторном клике - дубли постов!
```

**С `hx-swap-oob`:**

```
hx-target="#posts-list"       → Вставляются посты
hx-swap-oob на пагинаторе     → Пагинатор ОБНОВЛЯЕТСЯ
                              → Кнопка показывает page=3
                              → При клике - следующая порция!
```

### Как это работает технически?

**HTMX (JavaScript в браузере) при получении HTTP ответа ОТ СЕРВЕРА:**

1. **Парсит HTML**, полученный от Django
2. **Ищет элементы с атрибутом `hx-swap-oob`**
3. **Для каждого OOB элемента:**
   - Читает его `id` (например `id="pagination-controls"`)
   - Ищет **НА СТРАНИЦЕ** элемент с таким же `id`
   - Заменяет его **целиком** (по умолчанию `outerHTML`)
   - Замена = берёт HTML от сервера и вставляет вместо старого
4. **Остальные элементы** обрабатывает через `hx-target` и `hx-swap`

**❗ КЛЮЧЕВОЙ МОМЕНТ:**

HTMX **НЕ ВЫЧИСЛЯЕТ** номера страниц!  
HTMX **НЕ ЗНАЕТ** про пагинацию!  
HTMX просто **ТУПО ВСТАВЛЯЕТ HTML**, который сгенерировал Django!

**Пример:**

Если Django вернёт:

```html
<div id="pagination-controls" hx-swap-oob="true">
    <button hx-get="/posts/?page=999">Показать больше</button>
</div>
```

HTMX вставит **ИМЕННО** `page=999`, не задумываясь правильно это или нет!

Всю логику (вычисление номеров, проверка has_next) делает **DJANGO В ШАБЛОНЕ**!

---

## 🎨 Схема потока данных

```mermaid
sequenceDiagram
    participant User as 👤 Пользователь
    participant Browser as 🌐 Браузер (HTMX)
    participant Django as 🐍 Django
    participant Template as 📄 Шаблон

    User->>Browser: Клик "Показать больше"
    
    Note over Browser: HTMX читает атрибуты кнопки:<br/>hx-get="/posts/?page=2"<br/>hx-target="#posts-list"<br/>hx-swap="beforeend"<br/>hx-select=".post-card"
    
    Browser->>Django: GET /posts/?page=2<br/>(AJAX запрос)
    
    Note over Django: htmx_post_list_view()<br/>Получает page=2 из GET
    
    Django->>Django: Paginator(posts, 5).get_page(2)<br/>→ Посты 6-10<br/>→ page_obj.number = 2<br/>→ page_obj.next_page_number = 3
    
    Django->>Template: render(_posts_list.html, {<br/>"posts": посты 6-10,<br/>"page_obj": page_obj<br/>})
    
    Note over Template: Django подставляет значения:<br/>{{ post.title }} → "Пост 6"<br/>{{ page_obj.next_page_number }} → 3<br/>{{ page_obj.number }} → 2
    
    Template->>Django: HTML строка с подставленными значениями
    
    Django->>Browser: HTTP Response:<br/>&lt;div class="post-card"&gt;Пост 6&lt;/div&gt;<br/>&lt;div class="post-card"&gt;Пост 7&lt;/div&gt;<br/>...<br/>&lt;div id="pagination-controls" hx-swap-oob="true"&gt;<br/>&nbsp;&nbsp;&lt;button hx-get="/posts/?page=3"&gt;<br/>&lt;/div&gt;
    
    Note over Browser: HTMX парсит HTML<br/>Действие 1: hx-select находит .post-card<br/>Действие 2: Находит элемент с hx-swap-oob
    
    Browser->>Browser: Вставить .post-card в конец #posts-list
    Browser->>Browser: Заменить #pagination-controls<br/>на тот, что пришёл от сервера
    
    Browser->>User: ✅ Обновлённая страница:<br/>- 10 постов (5+5)<br/>- Кнопка показывает page=3<br/>- Активная: [2]
```

---

## 📊 Текстовая схема (если Mermaid не рендерится)

```
👤 ПОЛЬЗОВАТЕЛЬ
         |
         | (1) Клик "Показать больше"
         v
🌐 БРАУЗЕР (HTMX JavaScript)
         |
         | (2) Читает атрибуты кнопки:
         |     hx-get="/posts/?page=2"
         |     hx-target="#posts-list"
         |     hx-swap="beforeend"
         |     hx-select=".post-card"
         |
         | (3) Отправляет AJAX:
         |     GET /posts/?page=2
         v
🐍 DJANGO (views.py)
         |
         | (4) htmx_post_list_view(request)
         |     page = request.GET.get("page")  # "2"
         |
         | (5) Paginator(posts, 5).get_page(2)
         |     → Выбирает посты 6-10
         |     → page_obj.number = 2
         |     → page_obj.next_page_number = 3
         |
         | (6) render("_posts_list.html", context)
         v
📄 ШАБЛОН (_posts_list.html + _paginator.html)
         |
         | (7) Django ПОДСТАВЛЯЕТ значения:
         |     {{ post.title }} → "Пост 6", "Пост 7"...
         |     {{ page_obj.next_page_number }} → 3
         |     {{ page_obj.number }} → 2
         |
         | (8) Генерирует финальный HTML:
         |     <div class="post-card">Пост 6</div>
         |     <div class="post-card">Пост 7</div>
         |     ...
         |     <div id="pagination-controls" hx-swap-oob="true">
         |       <button hx-get="/posts/?page=3">...</button>
         |     </div>
         v
🐍 DJANGO
         |
         | (9) HTTP Response (обычный HTML текст)
         v
🌐 БРАУЗЕР (HTMX)
         |
         | (10) Парсит HTML от сервера
         |
         | (11) ДЕЙСТВИЕ 1:
         |      hx-select=".post-card" → Находит карточки
         |      hx-target="#posts-list" → Ищет контейнер
         |      hx-swap="beforeend" → Вставляет В КОНЕЦ
         |
         | (12) ДЕЙСТВИЕ 2:
         |      Видит hx-swap-oob="true" на #pagination-controls
         |      Ищет НА СТРАНИЦЕ элемент с id="pagination-controls"
         |      ЗАМЕНЯЕТ его на тот, что пришёл от сервера
         |
         | (13) Обновляет DOM
         v
👤 ПОЛЬЗОВАТЕЛЬ
         |
         | (14) Видит результат:
         |      ✅ 10 постов (старые + новые)
         |      ✅ Кнопка теперь ведёт на page=3
         |      ✅ Активная страница: [2]
```

---

## 🔑 КТО ЗА ЧТО ОТВЕЧАЕТ

| Компонент | Что делает | Что НЕ делает |
|-----------|------------|---------------|
| **HTMX** | • Отправляет AJAX запросы<br/>• Вставляет HTML от сервера<br/>• Заменяет элементы с `hx-swap-oob` | ❌ НЕ вычисляет номера страниц<br/>❌ НЕ знает про пагинацию<br/>❌ НЕ генерирует HTML |
| **Django Views** | • Получает параметр `page` из GET<br/>• Создаёт `Paginator`<br/>• Вычисляет `next_page_number`<br/>• Передаёт данные в шаблон | ❌ НЕ знает про HTMX<br/>❌ НЕ вставляет HTML в DOM |
| **Django Templates** | • Получает `page_obj` от view<br/>• Подставляет значения в `{{ }}`<br/>• Генерирует финальный HTML | ❌ НЕ отправляет запросы<br/>❌ НЕ вставляет в DOM |

---

## 📝 Чеклист: Что нужно для работы

### 1. В `main.html` (первая загрузка)

```html
<!-- Контейнер для постов -->
<div id="posts-list">
    {% for post in posts %}
        <div class="card post-card">{{ post.title }}</div>
    {% endfor %}
</div>

<!-- Пагинатор с уникальным id -->
<div id="pagination-controls">
    {% include 'core/_paginator.html' %}
</div>
```

### 2. В `_posts_list.html` (HTMX ответ)

```html
<!-- Посты (попадут в hx-target) -->
{% for post in posts %}
    <div class="card post-card">{{ post.title }}</div>
{% endfor %}

<!-- Пагинатор (обновится через OOB) -->
<div id="pagination-controls" hx-swap-oob="true">
    {% include 'core/_paginator.html' %}
</div>
```

**ВАЖНО:**

- `id="pagination-controls"` должен совпадать!
- `hx-swap-oob="true"` обязателен!

### 3. В `_paginator.html` (кнопка)

```html
<div id="pagination-controls" hx-swap-oob="true">
    {% if page_obj.has_next %}
    <button 
        hx-get="{% url 'core:post_list' %}?page={{ page_obj.next_page_number }}"
        hx-target="#posts-list"
        hx-swap="beforeend"
        hx-select=".post-card">
        Показать больше
    </button>
    {% endif %}
    
    <nav>
        {% for num in page_obj.paginator.page_range %}
            {% if page_obj.number == num %}[{{ num }}]{% else %}{{ num }}{% endif %}
        {% endfor %}
    </nav>
</div>
```

### 4. В `views.py`

```python
# Для полной страницы
def main_feed_view(request):
    page = request.GET.get("page", 1)
    page_obj = Paginator(posts, 5).get_page(page)
    return render(request, "core/main.html", {"posts": page_obj, "page_obj": page_obj})

# Для HTMX запросов
def htmx_post_list_view(request):
    page = request.GET.get("page", 1)
    page_obj = Paginator(posts, 5).get_page(page)
    return render(request, "core/_posts_list.html", {"posts": page_obj, "page_obj": page_obj})
```

### 5. В `_card.html`

```html
<div class="card post-card">  <!-- ВАЖНО: класс post-card! -->
    {{ post.title }}
</div>
```

---

## 🐛 Что проверить, если не работает?

### Проблема 1: Посты не добавляются

**Проверь:**

- В `_card.html` есть класс `post-card`
- В кнопке есть `hx-select=".post-card"`
- `hx-target="#posts-list"` правильный

### Проблема 2: Пагинатор не обновляется

**Проверь:**

- В `_paginator.html` есть `hx-swap-oob="true"`
- `id="pagination-controls"` одинаковый везде
- В `_posts_list.html` включён `_paginator.html`

### Проблема 3: Дубли пагинатора

**Проверь:**

- В `main.html` пагинатор НЕ внутри `#posts-list`
- В `_posts_list.html` пагинатор имеет `hx-swap-oob="true"`

### Проблема 4: Старые посты пропадают

**Проверь:**

- В кнопке `hx-swap="beforeend"` (НЕ `innerHTML`!)

---

## 💡 Простая аналогия

Представь, что HTMX — это почтальон:

**Обычная доставка:**

```
Ты: "Принеси мне пиццу"
Почтальон: *приносит пиццу в коробке*
Ты: *кладёшь пиццу на стол*
```

**OOB доставка:**

```
Ты: "Принеси мне пиццу"
Почтальон: *приносит пиццу в коробке*
           *И ЗАОДНО меняет вывеску на двери*
Ты: *кладёшь пиццу на стол*
    *замечаешь новую вывеску*
```

**Пиццу** = посты (идут в `hx-target`)  
**Вывеску** = пагинатор (меняется через `hx-swap-oob`)

Почтальон делает **два действия** за **одну поездку**!

---

## ✅ Итог

1. **Пользователь кликает** → HTMX отправляет запрос
2. **Django возвращает HTML** с постами и пагинатором
3. **HTMX делает два действия:**
   - Добавляет посты в конец списка
   - Заменяет пагинатор на новый
4. **Всё происходит без перезагрузки** страницы

**Главное:** `hx-swap-oob="true"` позволяет обновлять элементы **вне** основного `hx-target` за один запрос!
