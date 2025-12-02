from django import forms
from .models import *


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'excerpt',
            'body',
            # 'author',
            # 'date',
            'photo',
            'quotes',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان پست'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'خلاصه پست',
                'rows': 3
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'متن کامل پست',
                'rows': 10
            }),
            'quotes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'نقل قول (اختیاری)',
                'rows': 3
            }),
        }

class PostUpdateForm(forms.ModelForm):
    current_photo = forms.CharField(required=False, widget=forms.HiddenInput)
    class Meta:
        model = Post
        fields = ['title', 'excerpt', 'body', 'quotes', 'photo', 'is_active']
        widgets = {
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'onchange': 'previewImage(this)'
            }),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'quotes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.photo:
            self.fields['current_photo'].initial = self.instance.photo.url
            
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'نظر خود را اینجا بنویسید...',
                'rows': 4,
                'style': 'resize: none;'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].label = ''

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'پاسخ خود را اینجا بنویسید...',
                'rows': 3,
                'style': 'resize: none;'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].label = ''