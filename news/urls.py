from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
    path("", views.news_global_list, name="global_list"),
    path("like/<int:news_id>/", views.like_news, name="like_news"),
    path("<slug:slug>/", views.news_detail, name="detail"),
]
