from .models import Comment, Reply, Message, Post, Author
from django import forms
from ckeditor.fields import RichTextFormField
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth import get_user_model



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['email', 'body']

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['body']        
        
        
class PostForm(forms.ModelForm):
    class Meta:
        model = Post       
        fields = ['category', 'name', 'image', 'text', 'tags', 'videos']
        widgets =  {
            'text': CKEditorWidget(),
            
             
        }


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['email', 'about']
        


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['name', 'email', 'subject', 'messages']


class SearchForm(forms.Form):
    query = forms.CharField() 
