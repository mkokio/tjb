from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.feed, name="feed"),
    path("c/<slug:cat_slug>/", views.feed, name="category"),
    path("a/<slug:slug>/", views.article, name="article"),
    path("u/<slug:slug>/", views.profile, name="profile"),
    path("lang/", views.set_language, name="set_language"),
]
