"""View-файл содержит view-функции обработчики,
которые вызываются при запросе к URL в urlpatterns.
На вход принимает объект запроса HttpRequest, содержащий
данные о запросе: запрошенный URL, тип запроса и многое другое.
Возвращает бъект ответа HttpResponse, содержащий всю информацию,
которую должен получить веб-клиент: код ответа сервера,
код HTML-страницы и другую полезную для клиента информацию.
"""
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from posts.models import Post, Group, User
from posts.forms import PostForm


def index(request: HttpRequest) -> HttpResponse:
    """View-функция обработчик. Принимающая на вход объект
    запроса HttpRequest, возвращающая объект ответа HttpResponse.
    Возвращается Html-шаблон index.html
    """
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """View-функция обработчик. Принимающая на вход объект
    запроса HttpRequest, возвращающая объект ответа HttpResponse.
    Возвращается Html-шаблон group_list.html
    """
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """View-функция обработчик. Принимающая на вход объект
    запроса HttpRequest, возвращающая объект ответа HttpResponse.
    Возвращается Html-шаблон profile.html
    """
    title = f'Профайл пользователя {username}'
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related("group")
    post_count = posts.count()

    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'author': author,
        'posts': posts,
        'post_count': post_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request: HttpRequest, post_id: str) -> HttpResponse:
    """View-функция обработчик. Принимающая на вход объект
    запроса HttpRequest, возвращающая объект ответа HttpResponse.
    Возвращается Html-шаблон post_details.html
    """
    post = get_object_or_404(Post, pk=post_id)
    title = f'Пост {post.text}'
    author = post.author
    author_posts = author.posts
    post_count = author_posts.count()
    context = {
        'post': post,
        'title': title,
        'author': author,
        'post_count': post_count,
    }
    return render(request, 'posts/post_details.html', context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """View-функция обработчик. Принимающая на вход объект
    запроса HttpRequest, возвращающая объект ответа HttpResponse.
    Возвращается Html-шаблон post_create.html
    """
    title = 'Добавить запись'
    groups = Group.objects.all()
    form = PostForm(request.POST or None)
    context = {
        'title': title,
        'groups': groups,
        'form': form,
    }
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    post = form.save(commit=False)
    post.text = form.cleaned_data['text']
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user.username)


@login_required
def post_edit(request: HttpRequest, post_id: str) -> HttpResponse:
    """View-функция обработчик. Принимающая на вход объект
    запроса HttpRequest, возвращающая объект ответа HttpResponse.
    Возвращается Html-шаблон post_create.html
    """
    title = 'Редактировать запись'
    groups = Group.objects.all()
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST, instance=post)
    is_edit = True
    if post.author != request.user:
        return redirect('posts:profile', post.author)
    form = PostForm(request.POST or None, instance=post)
    context = {
        'title': title,
        'groups': groups,
        'post': post,
        'form': form,
        'is_edit': is_edit,
    }
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    post.author = request.user
    form.save()
    return redirect('posts:post_detail', post.pk)
