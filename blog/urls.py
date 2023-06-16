from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('blog/tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('blog/<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('blog/<int:post_id>/share/', views.PostShareView.as_view(), name='post_share'),
    path('blog/search/', views.post_search, name='post_search'),
]
