from django import forms
from .models import *


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'excerpt',
            'body',
            'author',
            'date',
            'quotes',
            'photo',
        ]

class PostUpdateForm(forms.ModelForm):
    current_photo = forms.CharField(required=False, widget=forms.HiddenInput)
    class Meta:
        model = Post
        fields = ['title', 'excerpt', 'body', 'quotes', 'photo']
        widgets = {
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'onchange': 'previewImage(this)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.photo:
            self.fields['current_photo'].initial = self.instance.photo.url
            
