from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('',views.main,name='main'),
    # profile
    path('users/<int:user_id>/',views.ProfileView.as_view(),name='profile'),
    path('users/<int:user_id>/reviews/',views.UserReviewListView.as_view(),name='user-review-list'),
    path('set-profile/',views.ProfileSetView.as_view(),name='profile-set'),
    path('edit-profile/',views.ProfileUpdateView.as_view(),name='profile-update'),

    # review
    path('reviews/<int:review_id>/',views.ReviewDetailView.as_view(),name='review-detail'),
    path('reviews/new/',views.ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:review_id>/edit/',views.ReviewUpdateView.as_view(),name='review-update'),
    path('reviews/<int:review_id>/delete/',views.ReviewDeleteView.as_view(),name='review-delete'),

   
    # account
    path('login/', views.loginview, name='login'),
    path('signup/', views.signup, name='signup'),

    path('search/', views.search, name='search'),  
]