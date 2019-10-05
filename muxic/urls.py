from django.urls import path

from . import views
from muxic.views import *

app_name = 'muxic'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user/<str:username>/', ProfileView.as_view(), name='user'),
    path('user/<str:username>/favorite/', ProfileFavoriteView.as_view(), name='user_fav'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('song/add/', SongCreate.as_view(), name='add_song'),
    path('song/<int:pk>/update/', SongUpdate.as_view(), name='update_song'),
    path('song/<int:pk>/delete/', SongDelete.as_view(), name='delete_song'),
    path('song/<int:pk>', SongDetailView.as_view(), name='songdetail'),
    path('all_song/', AllSong.as_view(), name='allsong'),
    path('search/', Search.as_view(), name='search'),
    path('favorite/<int:pk>/', FavoriteView.as_view(), name='favorite'),
    path('unfavorite/<int:pk>/', UnFavoriteView.as_view(), name='unfavorite'),
    path('genre/<str:genre>/', GenreFilter.as_view(), name='genre_filter')
]
