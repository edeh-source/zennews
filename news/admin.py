from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created', 'updated']
    list_filter = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 10



@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['user', 'created', 'updated'] 
    list_filter = ['user']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['name', 'category','slug', 'author', 'publish', 'active', 'created', 'updated']
    list_filter = ['name', 'category', 'slug', 'author', 'active',]
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 10    

@admin.register(Comment)   
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']  