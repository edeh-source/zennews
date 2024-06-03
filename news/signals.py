from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from .models import Post, Author

User = get_user_model()



@receiver(pre_save, sender=Post)
def create_slug(sender,instance, **kwargs):
    
    if not instance.slug:
        instance.slug = slugify(instance.name)
        
        
        
        

     