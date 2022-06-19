from django.urls import path
from . import views

urlpatterns = [

    # reviews urls
    path('', views.IndexView.as_view(), name='index'),
    path('search/', views.search, name='search'),
    path('<int:review_id>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('new/', views.ReviewCreateView.as_view(), name='review-create'),
    path('<int:review_id>/edit/', views.ReviewUpdateView.as_view(), name='review-update'),
    path('<int:review_id>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
    path('cateogry/<str:slug>/', views.categories_page),
    path('tags/<str:slug>/', views.tag_page),
    path('<int:review_id>/comment/',views.new_comment, name='create-comment'),
    path('<int:review_id>/comment/<int:comment_pk>/update/', views.comment_update, name='comment-update'),
    path('<int:review_id>/comment/<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),

    # profile urls
    path('users/<int:user_id>/', views.ProfileView.as_view(), name='profile'),
    path('users/<int:user_id>/reviews/', views.UserReviewListView.as_view(), name='user-review-list'),
    path('set-profile/', views.ProfileSetView.as_view(), name='profile-set'),
    path('edit-profile/', views.ProfileUpdateView.as_view(), name='profile-update'),
]