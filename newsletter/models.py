from django.db import models
from ckeditor.fields import RichTextField



class Subscribers(models.Model):
    email = models.EmailField(unique=True, db_index=True)

    def __str__(self):
        return self.email



class EmailTemplate(models.Model):
    subject = models.CharField(max_length=256)
    message =   RichTextField()
    recipients = models.ManyToManyField(Subscribers)  


    def __str__(self):
        return self.subject
        
    
