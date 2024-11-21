from django import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views 
from .views import MoviePostCreateView, MoviePostListView, MoviePostDetailView, MoviePostDeleteView, SignupView, LoginView, LogoutView, UserPostListView, AudioUploadView, DramaListView, AudioPostDeleteView

# name변수는 html에서 url에서 사용할 이름
urlpatterns = [
    path('', UserPostListView.as_view(), name='home'),
    path('posts/create/', MoviePostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/', MoviePostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/delete/', MoviePostDeleteView.as_view(), name='post_delete'),
    path('posts/', MoviePostListView.as_view(), name='post_list'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('audio/upload/', AudioUploadView.as_view(), name='audio_upload'),
    path('audio/', DramaListView.as_view(), name='audio_list'),
    path('audio/<int:pk>/delete/', AudioPostDeleteView.as_view(), name='audio_delete'),
    path('likes/<int:post_id>/', views.like_post, name="like_post"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)