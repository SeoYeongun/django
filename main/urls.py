from django import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views 
from .views import SignupView, LoginView, LogoutView, UserPostListView

# name변수는 html에서 url에서 사용할 이름
urlpatterns = [
    path('', UserPostListView.as_view(), name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('movie-list/', views.movie_list, name='movie_list'),
    path('load-more/', views.load_more_movies, name='load_more_movies'),
    path('daily-box-office/', views.daily_box_office, name='daily_box_office'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)