from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=Comment)
def create_comment_activity(sender, instance, created, **kwargs):
    if created:
        activity_type = 'reply' if instance.parent else 'comment'
        Activity.objects.create(
            user=instance.author,
            activity_type=activity_type,
            post=instance.post,
            comment=instance
        )

@receiver(m2m_changed, sender=Post.likes.through)
def create_post_like_activity(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            Activity.objects.create(
                user_id=user_id,
                activity_type='post_like',
                post=instance
            )

@receiver(m2m_changed, sender=Post.dislikes.through)
def create_post_dislike_activity(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            Activity.objects.create(
                user_id=user_id,
                activity_type='post_dislike',
                post=instance
            )

@receiver(m2m_changed, sender=Comment.likes.through)
def create_comment_like_activity(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            Activity.objects.create(
                user_id=user_id,
                activity_type='comment_like',
                post=instance.post,
                comment=instance
            )

@receiver(m2m_changed, sender=Comment.dislikes.through)
def create_comment_dislike_activity(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            Activity.objects.create(
                user_id=user_id,
                activity_type='comment_dislike',
                post=instance.post,
                comment=instance
            )