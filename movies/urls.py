from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('movies/<int:pk>/watchlist-toggle/', views.toggle_watchlist, name='toggle_watchlist'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('my-diary/', views.profile_view, name='my_diary'),
    path('user/<str:username>/', views.public_profile_view, name='public_profile'),
    path('register/', views.register_view, name='register'),
]

