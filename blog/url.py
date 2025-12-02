from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('post/new/', PostNewView.as_view(), name='post_new'),
    path('post/<int:pk>',PostDetailView.as_view(), name='post_detail'),
    path('post/update/<int:pk>',PostUpdateView.as_view(), name='update'),
    path('post/delete/<int:pk>',PostDeleteView.as_view(), name='delete'),
    path('post/<int:post_id>/comment/add/',AddCommentView.as_view(), name='add_comment'),
    path('comment/<int:comment_id>/edit/',UpdateCommentView.as_view(), name='update_comment'),
    path('comment/<int:comment_id>/delete/',DeleteCommentView.as_view(), name='delete_comment'),
    path('comment/<int:comment_id>/replies/',GetCommentRepliesView.as_view(), name='get_replies'),
    path('comment/<int:comment_id>/like/',ToggleCommentLikeView.as_view(), name='toggle_like'),
]
