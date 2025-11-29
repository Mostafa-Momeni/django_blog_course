from django.db import models
from datetime import date
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=255)
    excerpt = models.TextField()
    body = models.TextField()
    author = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    photo = models.ImageField(upload_to='photo/%Y/%m/%d/')
    quotes = models.TextField(max_length=255, null=True , blank=True)
    likes = models.ManyToManyField('accounts.CustomUser', related_name='post_likes', blank=True)
    dislikes = models.ManyToManyField('accounts.CustomUser', related_name='post_dislikes', blank=True)
    
    def dislikes_count(self):
        return self.dislikes.count()
    
    def likes_count(self):
        return self.likes.count()
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})
    