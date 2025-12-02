from django.contrib import admin
from .models import *


# admin.site.register(Post)
# admin.site.register(Comment)

class PostLikeInline(admin.TabularInline):
    model = PostLike
    extra = 0

class PostDislikeInline(admin.TabularInline):
    model = PostDislike
    extra = 0
    
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date', 'is_active', 'get_likes_count', 'get_dislikes_count', 'comments_count')
    list_filter = ('is_active', 'date', 'author')
    search_fields = ('title', 'body', 'author__username')
    readonly_fields = ('created_at','updated_at')
    inlines = [PostLikeInline, PostDislikeInline]
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'author', 'excerpt', 'body', 'photo')
        }),
        ('تنظیمات', {
            'fields': ('quotes', 'is_active', 'date')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_likes_count(self, obj):
        return obj.get_likes_count()
    get_likes_count.short_description = 'تعداد لایک‌ها'
    
    def get_dislikes_count(self, obj):
        return obj.get_dislikes_count()
    get_dislikes_count.short_description = 'تعداد دیسلایک‌ها'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_body', 'author', 'post', 'created_at', 'is_active', 'is_reply', 'get_replies_count')
    list_filter = ('is_active', 'created_at', 'post')
    search_fields = ('body', 'author__username', 'post__title')
    readonly_fields = ('created_at',)
    
    def short_body(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    short_body.short_description = 'متن نظر'
    
    def is_reply(self, obj):
        return '✅' if obj.parent else '❌'
    is_reply.short_description = 'پاسخ؟'
    
    def get_replies_count(self, obj):
        return obj.get_replies_count()
    get_replies_count.short_description = 'تعداد پاسخ‌ها'

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ('user__username', 'post__title')

@admin.register(PostDislike)
class PostDislikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ('user__username', 'post__title')

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created_at')
    list_filter = ('created_at', 'comment')
    search_fields = ('user__username', 'comment__body')

@admin.register(CommentDislike)
class CommentDislikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created_at')
    list_filter = ('created_at', 'comment')
    search_fields = ('user__username', 'comment__body')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_activity_type_display', 'post', 'comment', 'created_at')
    list_filter = ('activity_type', 'created_at', 'user')
    search_fields = ('user__username', 'post__title', 'comment__body')
    readonly_fields = ('created_at',)