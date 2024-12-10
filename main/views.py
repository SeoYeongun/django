from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.views import LogoutView as AuthLogoutView
from django.http import Http404
from django.contrib import messages
from .forms import PageForm, CommentForm
from .models import Post, Comment
from django.db.models import Q
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import requests
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from datetime import datetime
from django.core.paginator import Paginator
import random

class UserPostListView(ListView):
    model = Post
    template_name = 'main/base.html'  # 메인 페이지 템플릿 사용
    context_object_name = 'posts'
        
class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')  # 회원가입 후 이동할 URL

    def form_valid(self, form):
        response = super().form_valid(form)
        # 사용자 자동 로그인
        login(self.request, self.object)
        return response

class LoginView(AuthLoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True  # 로그인된 사용자 리다이렉트
    next_page = reverse_lazy('home')  # 로그인 후 이동할 URL

class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('home')  # 로그아웃 후 이동할 URL
    
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)  # post_id를 사용하여 Post 객체 가져오기

    if request.method == "POST":  # POST 요청으로 처리
        liked = False
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
            liked = True

        like_count = post.likes.count()

        return JsonResponse({'likes': liked, 'like_count': like_count})

    # GET 요청에 대해선 처리하지 않음 (없으면 404 오류 발생)
    return JsonResponse({'error': 'Invalid request method'}, status=400)




def get_movie_list(page=1, items_per_page=100):
    api_key = settings.MOVIE_API_KEY
    url = f'http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json?key={api_key}&curPage={page}&itemPerPage={items_per_page}'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        movies = data.get('movieListResult', {}).get('movieList', [])
        
        # 개봉일이 있는 영화만 최신순으로 정렬
        movies_with_open_date = [movie for movie in movies if movie.get('openDt') and is_valid_date(movie.get('openDt'))]
        sorted_movies = sorted(movies_with_open_date, key=lambda x: parse_date(x.get('openDt')), reverse=True)

        # 개봉일이 없는 영화는 랜덤으로 추가
        movies_without_open_date = [movie for movie in movies if not movie.get('openDt')]

        # 랜덤으로 개봉일 없는 영화와 최신 개봉일 영화들을 합침
        all_movies = sorted_movies + random.sample(movies_without_open_date, len(movies_without_open_date))  # 랜덤 샘플링
        return all_movies

    return []

def parse_date(date_str):
    # openDt가 비어있거나 형식이 잘못된 경우 처리
    if not date_str or len(date_str) != 8:
        return None  # 잘못된 날짜는 None으로 처리
    
    try:
        # openDt를 datetime 객체로 변환
        return datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        # 형식이 잘못된 경우 None 반환
        return None

def is_valid_date(date_str):
    # 날짜가 잘못된 형식인 경우를 필터링
    try:
        # 날짜가 유효한지 확인
        datetime.strptime(date_str, '%Y%m%d')
        return True
    except ValueError:
        return False

def movie_list(request):
    # 첫 번째 페이지 데이터를 가져오기
    page_number = int(request.GET.get('page', 1))
    movies = get_movie_list(page=page_number, items_per_page=100)

    # 영화 목록 페이지네이션 처리
    paginator = Paginator(movies, 100)
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/movie-list.html', {'page_obj': page_obj})

def load_more_movies(request):
    # AJAX로 요청된 페이지 번호 받기
    page_number = int(request.GET.get('page', 1))
    movies = get_movie_list(page=page_number, items_per_page=100)
    
    # 영화 데이터를 JSON 형식으로 반환
    return JsonResponse({'movies': movies})

def get_daily_box_office(date):
    api_key = settings.MOVIE_API_KEY
    url = f'http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={api_key}&targetDt={date}'
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('boxOfficeResult', {}).get('dailyBoxOfficeList', [])
    return []

def daily_box_office(request):
    today = datetime.now().strftime('%Y%m%d')  # 오늘 날짜를 YYYYMMDD 형식으로
    movies = get_daily_box_office(today)
    
    paginator = Paginator(movies, 10)  # 한 페이지에 10개 영화
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'main/daily-box-office.html', {'page_obj': page_obj})