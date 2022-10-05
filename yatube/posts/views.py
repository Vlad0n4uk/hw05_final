from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Follow, Group, Post, User
from posts.settings import (COUNT_POST_ON_PAGE, POST_CREATE_HTML,
                            POST_DETAIL_HTML, POST_EDIT_HTML,
                            POST_GROUP_LIST_HTML, POST_INDEX_HTML,
                            POST_PROFILE_HTML)


def page_obj(request, post_list):
    return Paginator(post_list, COUNT_POST_ON_PAGE).get_page(
        request.GET.get('page'))


def index(request):
    return render(request, POST_INDEX_HTML, {
        'page_obj': page_obj(request, Post.objects.all()),
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, POST_GROUP_LIST_HTML, {
        'group': group,
        'page_obj': page_obj(request, group.posts.all()),
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    return render(request, POST_PROFILE_HTML, {
        'author': author,
        'page_obj': page_obj(request, author.posts.all()),
        'following': request.user.is_authenticated and Follow.objects.filter(
            user=request.user,
            author=author).exists()
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
        'comments': post.comments.all()
    }
    return render(request, POST_DETAIL_HTML, context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {'form': form}
    if form.is_valid() is False:
        return render(request, POST_CREATE_HTML, context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, POST_EDIT_HTML, {
        'form': form,
        'is_edit': True,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    return render(request, 'posts/follow.html', {
        'page_obj': page_obj(request, posts)
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        if not Follow.objects.filter(
                author=author, user=request.user).exists():
            Follow.objects.create(
                author=author, user=request.user)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    author.following.filter(user=request.user).delete()
    return redirect('posts:profile', username)
