from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Post(models.Model):
    postname = models.CharField(max_length=50)
    contents = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 작성자 필드
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def total_likes(self):
        return self.likes.count()
    
    def __str__(self):
        return self.postname

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL) # 로그인하지 않은 사용자도 댓글 기능 사용 허락!!!
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username if self.author else 'Anonymous'} - {self.content}"
    
class Audio(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audios')
    title = models.CharField(max_length=100)
    audio_file = models.FileField(upload_to='audios/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title