from django.db import models
from datetime import date
from django.urls import reverse
from accounts.models import CustomUser

class Post(models.Model):
    title = models.CharField(max_length=200)
    excerpt = models.TextField()
    body = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    date = models.DateField(default=date.today)
    photo = models.ImageField(upload_to='posts/%Y/%m/%d/')
    quotes = models.TextField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(CustomUser, related_name='post_likes', blank=True, through='PostLike')
    dislikes = models.ManyToManyField(CustomUser, related_name='post_dislikes', blank=True, through='PostDislike')
    
    class Meta:
        ordering = ['-date', '-created_at']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})
    
    @property
    def comments_count(self):
        return self.comments.filter(is_active=True).count()
    
    def get_likes_count(self):
        return self.likes.count()
    
    def get_dislikes_count(self):
        return self.dislikes.count()
    
    def get_total_comments(self):
        """تعداد کل نظرات (شامل پاسخ‌ها)"""
        return self.comments.filter(is_active=True).count()
    
    def user_liked(self, user):
        """آیا کاربر این پست را لایک کرده است؟"""
        return self.likes.filter(id=user.id).exists()
    
    def user_disliked(self, user):
        """آیا کاربر این پست را دیسلایک کرده است؟"""
        return self.dislikes.filter(id=user.id).exists()
    
class PostLike(models.Model):
    """مدل واسط برای لایک پست"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_like_relations')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_post_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"

class PostDislike(models.Model):
    """مدل واسط برای دیسلایک پست"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_dislike_relations')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_post_dislikes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f"{self.user.username} disliked {self.post.title}"
    
class Comment(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='author')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_active = models.BooleanField(default=True)
    likes = models.ManyToManyField(CustomUser, related_name='comment_likes', blank=True, through='CommentLike')
    dislikes = models.ManyToManyField(CustomUser, related_name='comment_dislikes', blank=True, through='CommentDislike')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.post.pk}) + f'#comment-{self.id}'

    @property
    def is_reply(self):
        return self.parent is not None
    
    def get_replies(self):
        """دریافت تمام پاسخ‌های فعال"""
        return self.replies.filter(is_active=True).order_by('created_at')
    
    def get_replies_count(self):
        """تعداد پاسخ‌ها"""
        return self.replies.filter(is_active=True).count()
    
    def get_likes_count(self):
        """تعداد لایک‌ها"""
        return self.likes.count()
    
    def get_dislikes_count(self):
        """تعداد دیسلایک‌ها"""
        return self.dislikes.count()
    
    def user_liked(self, user):
        """آیا کاربر این کامنت را لایک کرده است؟"""
        return self.likes.filter(id=user.id).exists()
    
    def user_disliked(self, user):
        """آیا کاربر این کامنت را دیسلایک کرده است؟"""
        return self.dislikes.filter(id=user.id).exists()
    
    def get_comment_level(self):
        """سطح تو در تویی کامنت (0 = کامنت اصلی)"""
        level = 0
        current = self
        while current.parent:
            level += 1
            current = current.parent
        return level
    
class CommentLike(models.Model):
    """مدل واسط برای لایک کامنت"""
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_like_relations')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return f"{self.user.username} liked comment {self.comment.id}"

class CommentDislike(models.Model):
    """مدل واسط برای دیسلایک کامنت"""
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_dislike_relations')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_comment_dislikes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return f"{self.user.username} disliked comment {self.comment.id}"

class Activity(models.Model):
    """مدل برای ذخیره فعالیت‌های کاربران"""
    ACTIVITY_TYPES = (
        ('post_like', 'لایک پست'),
        ('post_dislike', 'دیسلایک پست'),
        ('comment_like', 'لایک کامنت'),
        ('comment_dislike', 'دیسلایک کامنت'),
        ('comment', 'نظر جدید'),
        ('reply', 'پاسخ جدید'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"