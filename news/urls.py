from django.urls import path

from news.views.posts import PostDetailView, PostListView


app_name = 'news'

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
]