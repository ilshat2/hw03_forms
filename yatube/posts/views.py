from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings

from posts.models import Post, Group, User
from posts.forms import PostForm


def index(request: HttpRequest) -> HttpResponse:
    """View-функция обработчик. Принимающая на вход объект
    запроса HttpRequest, возвращающая объект ответа HttpResponse.
    Возвращается Html-шаблон index.html.
    """
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.MAX)
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
    Возвращается Html-шаблон group_list.html.
    """
    group = get_object_or_404(Group, slug=slug)
    tittle = 'Записи соообщества'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.MAX)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'tittle': tittle
    }
    return render(request, 'posts/group_list.html', context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """View-функция обработчик. Принимающая на вход объект
    запроса HttpRequest, возвращающая объект ответа HttpResponse.
    Возвращается Html-шаблон profile.html.
    """
    title = f'Профайл пользователя {username}'
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related("group")
    post_count = posts.count()
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, settings.MAX)
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
    Возвращается Html-шаблон post_details.html.
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
    Возвращается Html-шаблон post_create.html.
    """
    title = 'Добавить запись'
    groups = Group.objects.all()
    form = PostForm()
    context = {
        'title': title,
        'groups': groups,
        'form': form,
    }
    if request.method != 'POST':
        return render(request, 'posts/create_post.html', context)
    form = PostForm(request.POST or None)
    post = form.save(commit=False)
    post.author = request.user
    if request.user != post.author:
        return render(request, 'posts/create_post.html', context)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    form.save()
    return redirect('posts:profile', username=request.user.username)


@login_required
def post_edit(request: HttpRequest, post_id: str) -> HttpResponse:
    """View-функция обработчик. Принимающая на вход объект
    запроса HttpRequest, возвращающая объект ответа HttpResponse.
    Возвращается Html-шаблон post_create.html.
    """
    title = 'Редактировать запись'
    groups = Group.objects.all()
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    form = PostForm(request.POST, instance=post)
    if request.method != 'POST':
        form = PostForm(instance=post)
    post.author = request.user
    context = {
        'title': title,
        'groups': groups,
        'post': post,
        'is_edit': is_edit,
        'form': form
    }
    if post.author != request.user:
        return redirect('posts:profile', post.author)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    form.save()
    return redirect('posts:post_detail', post.pk)
