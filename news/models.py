from django.db import models
from users.models import User

from django.utils.text import slugify
from PIL import Image
from embed_video.fields import EmbedVideoField
from taggit.managers import TaggableManager
import cv2
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.contrib.auth import get_user_model
from django.conf import settings



class Category(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    slug = models.SlugField(max_length=256)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('category_details', args=[self.slug])    
    
    class Meta:
        ordering = ['-created']
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    

class Author(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authors',)
    email = models.EmailField(blank=True)
    about = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username    

class Post(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='posts')
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique_for_date='publish', blank=True)
    active = models.BooleanField(default=False)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name='posts')
    publish = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='posts_images')
    text = RichTextField()
    views = views = models.PositiveIntegerField(default=0)
    tags = TaggableManager()
    videos = EmbedVideoField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    
    


    def get_absolute_url(self):
        return reverse('post_details', args=[self.id, self.slug, self.publish.year, self.publish.month, self.publish.day])
    
    def get_publisher_url(self):
        return reverse('publisher_details', args=[self.id, self.slug, self.publish.year, self.publish.month, self.publish.day])


    def __str__(self):
        return self.name
    
    
    


    

    def save(self, *args, **kwargs):       
        super().save(*args, **kwargs) 
        img = cv2.imread(self.image.path)
        height, width = 630, 900
        dim = (width, height)
        resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        cv2.imwrite(self.image.path, resized_img)
        

    

class Comment(models.Model):
    post = models.name = models.ForeignKey('Post', related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(to='users.User', related_name='comments', on_delete=models.CASCADE, default='ba94a1b9-8dce-4e5c-a0df-be383b13a070')
    name = models.CharField(max_length=80, blank=True, null=True)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)


    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post} on {self.body}'



class Reply(models.Model):
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(to='users.User', on_delete=models.CASCADE, related_name='replies')
    body = models.TextField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Reply by {self.user} on {self.comment} '
        

class Message(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    email = models.EmailField()
    subject = models.CharField()
    messages = models.TextField()

    def __str__(self):
        return f'Message by {self.name} and {self.email}'
        
                
    