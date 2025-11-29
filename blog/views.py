from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import *
from .forms import *

class HomeView(ListView):
    model = Post
    template_name = 'home.html'
        
class PostDetailView(DetailView):
    model = Post
    template_name = 'single_post.html'
 
class PostNewView(CreateView):
    model = Post
    template_name = 'post_new.html'
    form_class = PostForm
    success_url = reverse_lazy('home')
    
class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_update.html'
    form_class = PostUpdateForm
    
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('home')