from django.views.generic import View, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from .models import *
from .forms import *



class HomeView(View):
    # model = Post
    template_name = 'home.html'
    paginate_by = 1
    
    def get(self, request):
        posts = Post.objects.all()
        paginator = Paginator(posts, self.paginate_by)
        
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'post_list':page_obj
        }
        
        return render(request,self.template_name,context)
        
        
class PostDetailView(DetailView):
    model = Post
    template_name = 'single_post.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(parent=None, is_active=True)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'برای ثبت نظر باید وارد شوید'
            }, status=401)
        
        # دریافت داده‌های فرم
        body = request.POST.get('body', '').strip()
        
        if not body:
            return JsonResponse({
                'success': False,
                'error': 'متن نظر نمی‌تواند خالی باشد'
            }, status=400)
        
        # ایجاد نظر جدید (نظر اصلی، نه پاسخ)
        try:
            comment = Comment.objects.create(
                post=self.object,
                author=request.user,
                body=body
            )
            
            return JsonResponse({
                'success': True,
                'message': 'نظر شما با موفقیت ثبت شد',
                'comment_id': comment.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

 
class PostNewView(CreateView):
    model = Post
    template_name = 'post_new.html'
    form_class = PostForm
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        # تنظیم author به صورت خودکار از کاربر لاگین کرده
        form.instance.author = self.request.user
        messages.success(self.request, 'پست با موفقیت ایجاد شد.')
        return super().form_valid(form)
    
class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_update.html'
    form_class = PostUpdateForm
    
    def get_success_url(self):
        messages.success(self.request, 'پست با موفقیت بروزرسانی شد.')
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            messages.error(request, 'شما اجازه ویرایش این پست را ندارید.')
            return redirect('post_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)
    
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            messages.error(request, 'شما اجازه حذف این پست را ندارید.')
            return redirect('post_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'پست با موفقیت حذف شد.')
        return super().delete(request, *args, **kwargs)
    
    
# ==============================================
# ویوهای مربوط به نظرات (Comments)
# ==============================================

class AddCommentView(LoginRequiredMixin, View):
    """ویو برای افزودن نظر جدید"""
    
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        
        body = request.POST.get('body', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if not body:
            return JsonResponse({
                'success': False,
                'error': 'لطفا متن نظر را وارد کنید'
            }, status=400)
            
        try:
            # ایجاد نظر جدید
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id, post=post)
                comment = Comment.objects.create(
                    post=post,
                    author=request.user,
                    body=body,
                    parent=parent_comment
                )
            else:
                comment = Comment.objects.create(
                    post=post,
                    author=request.user,
                    body=body
                )
            
            # آماده کردن پاسخ
            response_data = {
                'success': True,
                'message': 'نظر شما با موفقیت ثبت شد.',
                'comment': self.get_comment_data(comment)
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def get_comment_data(self, comment):
        """تبدیل کامنت به دیکشنری برای پاسخ JSON"""
        # آدرس آواتار پیش‌فرض
        default_avatar = '/static/assets/img/comment/comment_1.png'
        avatar_url = default_avatar
        
        # تلاش برای دریافت آواتار کاربر
        try:
            if hasattr(comment.author, 'photo') and comment.author.photo:
                avatar_url = comment.author.photo.url
        except:
            pass
        
        return {
            'id': comment.id,
            'body': comment.body,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'author': {
                'id': comment.author.id,
                'username': comment.author.username,
                'avatar': avatar_url
            },
            'parent_id': comment.parent.id if comment.parent else None
        }

class UpdateCommentView(LoginRequiredMixin, View):
    """ویو برای ویرایش نظر"""
    
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        
        # بررسی مالکیت
        if comment.author != request.user:
            return JsonResponse({
                'success': False,
                'error': 'شما مجاز به ویرایش این نظر نیستید'
            }, status=403)
        
        try:
            data = json.loads(request.body) if request.body else request.POST
            body = data.get('body', '').strip()
            
            if not body:
                return JsonResponse({
                    'success': False,
                    'error': 'لطفا متن نظر را وارد کنید'
                }, status=400)
            
            comment.body = body
            comment.save()
            
            return JsonResponse({
                'success': True,
                'message': 'نظر با موفقیت ویرایش شد.',
                'comment': {
                    'id': comment.id,
                    'body': comment.body
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

class DeleteCommentView(LoginRequiredMixin, View):
    """ویو برای حذف نظر"""
    
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        
        # بررسی مالکیت
        if comment.author != request.user and not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'شما مجاز به حذف این نظر نیستید'
            }, status=403)
        
        try:
            post_id = comment.post.id
            comment_id = comment.id
            comment.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'نظر با موفقیت حذف شد',
                'comment_id': comment_id,
                'post_id': post_id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

class GetCommentRepliesView(View):
    """دریافت پاسخ‌های یک کامنت"""
    
    def get(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        replies = comment.replies.all().order_by('created_at')
        
        replies_data = []
        for reply in replies:
            replies_data.append({
                'id': reply.id,
                'body': reply.body,
                'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'author': {
                    'id': reply.author.id,
                    'username': reply.author.username,
                    'avatar': self.get_avatar_url(reply.author)
                }
            })
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'body': comment.body,
                'author': comment.author.username,
                'created_at': comment.created_at.isoformat(),
            },
            # 'replies': replies_data,
            # 'count': replies.count()
        })
    
    def get_avatar_url(self, user):
        """دریافت آدرس آواتار کاربر"""
        default_avatar = '/static/assets/img/comment/comment_1.png'
        try:
            if hasattr(user, 'profile') and user.profile.photo:
                return user.profile.photo.url
        except:
            pass
        return default_avatar

class ToggleCommentLikeView(LoginRequiredMixin, View):
    """لایک/دیسلایک کامنت"""
    
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        action = request.POST.get('action', 'like')  # like or dislike
        
        # ایجاد یا به‌روزرسانی لایک
        like, created = CommentLike.objects.get_or_create(
            comment=comment,
            user=request.user,
            defaults={'is_like': action == 'like'}
        )
        
        if not created:
            # اگر از قبل وجود داشت، مقدار را تغییر می‌دهیم
            like.is_like = action == 'like'
            like.save()
        
        # تعداد لایک‌ها و دیسلایک‌ها
        likes_count = comment.likes.filter(is_like=True).count()
        dislikes_count = comment.likes.filter(is_like=False).count()
        
        return JsonResponse({
            'success': True,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
            'user_action': 'like' if like.is_like else 'dislike'
        })