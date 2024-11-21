# forms.py
from django import forms
from .models import Post, Comment, Audio

class PageForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'postname', 'contents']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class AudioForm(forms.ModelForm):
    class Meta:
        model = Audio
        fields = ['title', 'audio_file', 'description']