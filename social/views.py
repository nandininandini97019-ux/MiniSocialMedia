from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Exists, OuterRef

from .models import Post, Comment, Like, Follow
from .forms import RegisterForm, PostForm, CommentForm, ProfileForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("feed")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account was created!")
        return redirect("feed")

    return render(request, "registration/register.html", {
        "form": form,
    })


@login_required
def feed_view(request):
    posts = (
        Post.objects
        .select_related("author", "author__profile")
        .annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
            liked_by_me=Exists(
                Like.objects.filter(
                    post=OuterRef("pk"),
                    user=request.user
                )
            ),
        )
    )

    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list("following_id", flat=True)

    return render(request, "social/feed.html", {
        "posts": posts,
        "post_form": PostForm(),
        "comment_form": CommentForm(),
        "following_ids": following_ids,
    })


@login_required
@require_POST
def create_post(request):
    form = PostForm(request.POST, request.FILES)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "Your post was published!")
    else:
        messages.error(request, "Please enter a caption of up to 2000 characters.")

    return redirect("feed")


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect("feed")


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    like, created = Like.objects.get_or_create(
        post=post,
        user=request.user
    )

    if not created:
        like.delete()

    return redirect("feed")


@login_required
@require_POST
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)

    if target == request.user:
        messages.error(request, "You cannot follow yourself.")
        return redirect("profile", username=username)

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target
    )

    if not created:
        follow.delete()

    return redirect("profile", username=username)


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(
        User.objects.select_related("profile"),
        username=username
    )

    posts = (
        Post.objects
        .filter(author=profile_user)
        .annotate(likes_count=Count("likes", distinct=True))
    )

    is_following = Follow.objects.filter(
        follower=request.user,
        following=profile_user
    ).exists()

    return render(request, "social/profile.html", {
        "profile_user": profile_user,
        "posts": posts,
        "is_following": is_following,
        "followers_count": Follow.objects.filter(
            following=profile_user
        ).count(),
        "following_count": Follow.objects.filter(
            follower=profile_user
        ).count(),
        "is_own_profile": request.user == profile_user,
    })


@login_required
def edit_profile(request):
    profile = request.user.profile
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated!")
        return redirect("profile", username=request.user.username)

    return render(request, "social/edit_profile.html", {
        "form": form,
    })
