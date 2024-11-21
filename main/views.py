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

class UserPostListView(ListView):
    model = Post
    template_name = 'main/base.html'  # 메인 페이지 템플릿 사용
    context_object_name = 'posts'
    paginate_by = 10  # 페이지당 게시물 수 설정

    def get_queryset(self):
        # 기본값으로 모든 게시물을 반환
        query = self.request.GET.get('q', '').strip()  # 기본값을 ''로 설정하고 앞뒤 공백 제거
        print(f'Search query: "{query}"')  # 검색어 출력 (디버깅용)

        # 검색어가 있는 경우 검색 결과 반환
        if query:
            return Post.objects.filter(
                Q(postname__icontains=query) | Q(contents__icontains=query)
            ).distinct().order_by('-created_at')

        # 로그인한 사용자일 경우 사용자 게시물 반환
        if self.request.user.is_authenticated:
            user_posts = Post.objects.filter(author=self.request.user)
            return user_posts.distinct().order_by('-created_at')

        # 비로그인 사용자에게는 모든 게시물 반환
        return Post.objects.all().order_by('-created_at')

class MoviePostCreateView(CreateView, LoginRequiredMixin):
    model = Post
    form_class = PageForm
    template_name = 'main/PostCreateView.html'
    success_url = reverse_lazy('post_list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user  # 현재 사용자 설정
        return super().form_valid(form)  # 폼 유효성 검사 후 저장

class MoviePostListView(ListView):
    model = Post
    template_name = 'main/PostListView.html'
    context_object_name = 'posts'
    paginate_by = 10

class MoviePostDetailView(DetailView):
    model = Post
    template_name = 'main/PostDetailView.html'
    context_object_name = 'post'

    def post(self, request, *args, **kwargs):
        post = self.get_object()  # 현재 게시물 객체 가져오기

        # 좋아요 처리
        if 'like' in request.POST:
            if post.likes.filter(id=request.user.id).exists():
                post.likes.remove(request.user)  # 좋아요 취소
            else:
                post.likes.add(request.user)  # 좋아요 추가
            # 좋아요 상태가 변경된 후 페이지 새로 고침
            return redirect('post_detail', pk=post.pk)

        # 댓글 작성 처리
        elif 'content' in request.POST:  # 'content'가 있는 경우 댓글 작성 처리
            content = request.POST.get('content')
            if content:
                comment = Comment.objects.create(
                    post=post,
                    author=request.user if request.user.is_authenticated else None,
                    content=content
                )
                comment.save()
                return redirect('post_detail', pk=post.pk)  # 댓글 작성 후 페이지 새로 고침

        # 잘못된 경우 기본 리디렉션
        return redirect('post_detail', pk=post.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 게시물에 대한 댓글 가져오기
        context['comments'] = self.object.comments.all()  # 게시물에 달린 댓글
        context['form'] = CommentForm()  # 댓글 작성 폼 추가
        return context

class MoviePostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'main/PostDeleteView.html'
    context_object_name = 'post'
    success_url = reverse_lazy('post_list')

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, '이 게시물을 삭제할 권한이 없습니다.')
            return redirect('post_detail', pk=post.pk)  # 권한이 없으면 상세 페이지로 리디렉션
        return super().get(request, *args, **kwargs)  # 권한이 있으면 삭제 확인 페이지를 보여줌

    def delete(self, request, *args, **kwargs):
        messages.success(request, '게시물이 삭제되었습니다.')
        return super().delete(request, *args, **kwargs)  # 삭제 진행
        
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

# Audio
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .models import Audio
from .forms import AudioForm


class AudioUploadView(LoginRequiredMixin, CreateView):
    model = Audio
    fields = ['title', 'audio_file', 'description']
    template_name = 'main/audio_upload.html'
    success_url = reverse_lazy('audio_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class DramaListView(ListView):
    model = Audio
    template_name = 'main/audio_list.html'
    context_object_name = 'audios'


class AudioPostDeleteView(LoginRequiredMixin, DeleteView):
    model = Audio
    template_name = 'main/audio_post_confirm_delete.html'
    context_object_name = 'audio'
    success_url = reverse_lazy('audio_list') 

    def get_queryset(self):
        # 현재 로그인한 사용자가 본인 게시물만 삭제할 수 있도록 필터링
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)
    

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