'''@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': page_obj(request, post_list)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    profile_author = get_object_or_404(User, username=username)
    Follow.objects.create(user=request.user, author=profile_author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    author.following.filter(user=request.user).delete()
    return redirect('posts:profile', username)

@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.select_related('follower').get()
    if is_follower.exclude(author) and is_follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.select_related('follower').get()
    if is_follower.exclude(author) and is_follower.exists():
        Follow.objects.delete(user=user, author=author)
    return redirect('posts:profile', username)'''