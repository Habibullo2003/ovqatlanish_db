from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
# Create your models here.

class Article(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=200)
    body = models.TextField()
    photo = models.ImageField(upload_to='images/', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('article_detail', args={str(self.pk)})