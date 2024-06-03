from django.urls import path
from . import views



urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('category/<slug:slug>/', views.Category_details.as_view(), name='category_details'),
    path('author/<str:username>/', views.Author_posts.as_view(), name='authors_posts'),
    path('tags/<slug:slug>/', views.Tag_Detail.as_view(), name='tag_details'),
    path('reply/<int:reply>/', views.post_details, name='reply_details'),
    path('mine/', views.ManagePostListView.as_view(), name='manage_post_list'),
    path('comment_reply/<int:id>/', views.reply_comment, name='comment_reply'),
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('post_create/', views.create_post, name='create_post'),
    path('<int:id>/post_edit/', views.edit_post, name='post_edit'),
    path('<pk>/edit/', views.PostUpdateView.as_view(), name='post_update'),
    path('<pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('publisher/<int:id>/<slug:slug>/<int:year>/<int:month>/<int:day>/', views.publisher_details, name='publisher_details'),
    path('contact/', views.message_admin, name='message_admin'),
    path('search/', views.post_search, name='post_search'),
    path('author/', views.Author_Form, name='author'),
    path('searches/', views.PostSearchView.as_view(), name='search'),
    path('details/<int:id>/<slug:slug>/<int:year>/<int:month>/<int:day>/', views.post_details, name='post_details'),
]