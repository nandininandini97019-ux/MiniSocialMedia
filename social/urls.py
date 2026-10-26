from django.urls import path
from . import views

urlpatterns = [
    path("", views.feed_view, name="feed"),
    path("register/", views.register_view, name="register"),

    path("post/create/", views.create_post, name="create_post"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("post/<int:post_id>/like/", views.toggle_like, name="toggle_like"),

    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.profile_view, name="profile"),
    path("profile/<str:username>/follow/", views.toggle_follow, name="toggle_follow"),
]