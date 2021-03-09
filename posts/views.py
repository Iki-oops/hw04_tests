from django.shortcuts import render, get_object_or_404, redirect
from django. contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm
# from rest_framework import paginator


def index(request):
    posts = Post.objects.all()
    # paginator = paginator.Paginator(posts)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'group': group, 'page': page, 'paginator': paginator}
    return render(request, 'group.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'author': author,
        'author_posts': author_posts,
        'paginator': paginator,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    context = {
        'author': post.author,
        'post': post,
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)

    group = post.group

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=post.author.username, post_id=post.id)

    context = {
        'post': post,
        'group': group,
        'form': form
    }
    return render(request, 'post_edit.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('index')

    context = {'form': form}
    return render(request, 'new_post.html', context)
