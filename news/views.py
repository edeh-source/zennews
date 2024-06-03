from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.views.generic.list import ListView
from django.views.generic.base import TemplateResponseMixin
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchHeadline, SearchRank
from taggit.models import Tag
from django.views.generic.edit import FormView
from django.contrib.postgres.search import TrigramSimilarity
from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector
from .forms import PostForm, SearchForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.db.models import Count
from django.views.generic import FormView
from django.views import View
from django.contrib.auth import get_user_model
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .models import Post
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author
from .forms import CommentForm, ReplyForm, MessageForm, SearchForm, AuthorForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group

class HomePage(ListView):
    model = Post
    template_name = 'news/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        #category = Category.objects.get(name='Trending News')
        return Post.objects.filter(category__name='Trending News', active=True).order_by('-publish')[:5]
    
    

def post_details(request, id, slug, year, month, day, reply=None):
    post = get_object_or_404(Post, id=id, slug=slug, publish__year=year, publish__month=month, publish__day=day, active=True)
    request.session['post_title'] = post.name
    post.views += 1
    post.save()
    related_tags = post.tags.all()
    comments = post.comments.filter(active=True)
    user = request.user
    similiar_post = None
    comment = None
    replies = None
    if reply:
        reply = get_object_or_404(Reply, id=reply)
        replies = reply.comment.filter(active=True)
        
    else:
        pass    
        
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            messages.success(request, 'COMMENT SUBMITTED SUCCESFULLY')
        else:
            messages.error(request, 'CORRECT THE ERROR BELOW') 
    else:
        form = CommentForm()  
        post_tags_ids = post.tags.values_list('id', flat=True)
        similiar_post = Post.objects.filter(tags__in=post_tags_ids, active=True).exclude(id=post.id)
        similiar_post = similiar_post.annotate(same_tags=Count('tags')).order_by('-same_tags', 'active')[:4]
        

    return render(request, 'news/single-post.html', {'post': post, 'related_tags': related_tags, 'form': form, 'comment': comment, 'comments': comments, 'user': user, 'replies': replies, 'similiar_post': similiar_post})   


def publisher_details(request, id, slug, year, month, day):
    post = get_object_or_404(Post, id=id, slug=slug, publish__year=year, publish__month=month, publish__day=day)
    return render(request, 'news/manage/detail.html', {'post': post})


def get_categories(request):
    category = Category.objects.all()    
    return {'category': category}



class Category_details(ListView):
    model = Post
    template_name = 'news/category.html'
    context_object_name = 'post_cate'
    paginate_by = 4

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        posts = Post.objects.filter(category=category, active=True).order_by('-created')
        return posts


class Author_posts(ListView):
    model = Post
    template_name = 'news/author.html'
    context_object_name = 'author_cate'
    paginate_by = 4

    def get_queryset(self):
        author = get_object_or_404(Author, user__username=self.kwargs['username'])
        print(author)
        posts = Post.objects.filter(author=author, active=True).order_by('-publish')
        return posts
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_post"] = get_object_or_404(Author, user__username=self.kwargs['username'])
        return context
    

class Tag_Detail(ListView):
    model = Post
    template_name = 'news/tag.html'
    context_object_name = 'tags'
    paginate_by = 1

    def get_queryset(self):
        tags = get_object_or_404(Tag, slug=self.kwargs['slug'])
        post_tags = Post.objects.filter(tags=tags)
        return post_tags


def recent_posts(request):
    recent = Post.objects.filter(active=True).order_by('-publish')[:7]
    return {'recent': recent}


def reply_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    reply = None
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
           reply = form.save(commit=False)
           reply.user = request.user
           reply.comment = comment
           reply.save()
           post = comment.post
           messages.success(request, 'Replied Succesfully')
           return redirect('post_details', id=post.id, slug=post.slug, year=post.publish.year, month=post.publish.month, day=post.publish.day)
        else:
            messages.error(request, 'Correct The Error Below')
    else:
        form = ReplyForm()
    return render(request, 'news/reply.html', {'reply': reply, 'form': form })   



def message_admin(request):
    if request.method == 'POST':
        contact =  MessageForm(request.POST)
        if contact.is_valid():
            contact.save()
            messages.success(request, 'MESSAGE SUBMITTED SUCCESFULLY')
        else:
            messages.error(request, 'CORRECT THE ERROR BELOW')
    else:
        contact = MessageForm()
    return render(request, 'news/contact.html', {'contact': contact })                              


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    

    if 'query' in request.GET:
        print(request.GET)
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.objects.annotate(
                search=SearchVector('name', 'text'),
            ).filter(search=query).order_by('-created')

    return render(request,
                  'news/search-result.html',
                  {'form': form,
                   'query': query,
                   'results': results})   


 
        




class PostSearchView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "news/search-result.html"
    


    def get_queryset(self):
        query = self.request.GET.get("q")
        search_vector = SearchVector("name", "text")
        search_query = SearchQuery(query)
        search_headline = SearchHeadline("text", search_query)
        return Post.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).annotate(headline=search_headline).filter(search=search_query).order_by("-rank")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        return context
        




def most_popular_post(request):
    posts = Post.objects.order_by('-views')[:5]
    most_popular_posts = list(posts)
    return {'most_popular_posts': most_popular_posts}

def get_one_culture(request):
    culture_category = Category.objects.get(name='Culture')
    post_culture = Post.objects.filter(category=culture_category, active=True).order_by('-publish')[:1]
    return {'post_culture': post_culture, 'culture_category': culture_category }


def all_posts(request):
    all_post = Post.objects.filter(active=True).order_by('-publish')[:9]
    return {'all_post': all_post }
    

def get_one_trending_news(request):
    trend_category = Category.objects.get(name='Trending News')
    post_trend = Post.objects.filter(category=trend_category, active=True).order_by('-publish')[:1]
    return {'post_trend': post_trend, 'trend_category': trend_category }


def get_all_trending_posts(request):
    all_trend_post = Post.objects.filter(category__name='Trending News', active=True).order_by('-publish')[:9]
    return {'all_trend_post': all_trend_post} 


def get_one_buisness_news(request):
    buisness_category = Category.objects.get(name='Buisness')
    buisness_trend = Post.objects.filter(category=buisness_category, active=True).order_by('-publish')[:1]
    return {'buisness_trend': buisness_trend, 'buisness_category': buisness_category }


def get_all_buisness_posts(request):
    all_buisness_post = Post.objects.filter(category__name='Buisness', active=True).order_by('-publish')[:9]
    return {'all_buisness_post': all_buisness_post}     


def get_one_sports_news(request):
    sports_category = Category.objects.get(name='Sports')
    sports_trend = Post.objects.filter(category=sports_category, active=True).order_by('-publish')[:1]
    return {'sports_trend': sports_trend, 'sports_category': sports_category }


def get_all_sports_posts(request):
    all_sports_post = Post.objects.filter(category__name='Sports', active=True).order_by('-publish')[:9]
    return {'all_sports_post': all_sports_post} 


def get_one_international(request):
    one_international_category = Category.objects.get(name='International News')
    post_international = Post.objects.filter(category=one_international_category, active=True).order_by('-publish')[:1]
    return {'post_international': post_international, 'one_international_category': one_international_category}

def get_all_international(request):
    all_international = Post.objects.filter(category__name='International News', active=True).order_by('-publish')[:9]
    return {'all_international': all_international }

def get_one_health_news(request):
    health_category = Category.objects.get(name='Health')
    post_health = Post.objects.filter(category=health_category, active=True).order_by('-publish')[:1]
    return {'post_health': post_health, 'health_category': health_category }


def get_all_health(request):
    all_health_post = Post.objects.filter(category__name='Health', active=True).order_by('-publish')[:9]
    return {'all_health_post': all_health_post} 


def trending_news(request):
    trend_category = Category.objects.get(name='Trending News')
    post_trend_news = Post.objects.filter(category=trend_category, active=True).order_by('-publish')[:5]
    return {'post_trend_news': post_trend_news, 'trend_category': trend_category }


def get_latest_posts(request):
    all_latest_post = Post.objects.filter(active=True).order_by('-publish')[:5]
    return {'all_latest_post': all_latest_post}       
             


class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(author__user=self.request.user).order_by('-publish')
    
    
class OwnerEditMixin:
    def form_valid(self, form):
        author = Author.objects.get_or_create(user=self.request.user)[0]
        print(author)
        form.instance.author = author
        return super().form_valid(form)
    
class OwnerPostMixin(OwnerMixin, FormView, LoginRequiredMixin, PermissionRequiredMixin):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('manage_post_list')
    

class OwnerPostEditMixin(OwnerPostMixin, OwnerEditMixin):
    template_name = 'news/manage/form.html'
    
class ManagePostListView(OwnerPostMixin, ListView):
    paginate_by = 9
    template_name = 'news/manage/list.html'
    permission_required = 'news.view_post'
    
    
class PostCreateView(OwnerPostEditMixin, CreateView):
        permission_required = 'news.add_post'
    
class PostUpdateView(OwnerPostEditMixin, UpdateView):
        permission_required = 'news.change_post'
    
class PostDeleteView(DeleteView, PermissionRequiredMixin):
    model = Post
    context_object_name = 'post'
    template_name = 'news/manage/delete.html'
    permission_required = 'news.delete_post'
    success_url = reverse_lazy('manage_post_list')
    
     
@permission_required('news.add_post')     
@login_required
def create_post(request):
    author = Author.objects.get(user=request.user)
    if request.method == 'POST':
        form_post = PostForm(request.POST, request.FILES)
        if form_post.is_valid():
            user_author = form_post.save(commit=False)
            user_author.author = author
            user_author.save()
            messages.success(request, 'POST CREATED SUCCESFULLY')
            return redirect('manage_post_list')
        else:
            messages.error(request, 'Correct The Error Below')   
    else:
        form_post = PostForm()
    return render(request, 'news/manage/form.html', {'form_post': form_post })  


    
@permission_required('news.change_post')
@login_required
def edit_post(request, id):
    author = Author.objects.get(user=request.user)
    post_update = Post.objects.get(id=id, author=author)
    if request.method == 'POST':
        form_post = PostForm(instance=post_update,  data=request.POST, files= request.FILES)
        if form_post.is_valid():
            user_author = form_post.save(commit=False)
            user_author.author = author
            user_author.save()
            messages.success(request, 'POST UPDATED SUCCESFULLY')
            return redirect('manage_post_list')
        else:
            messages.error(request, 'Correct The Error Below')   
    else:
        form_post = PostForm(instance=post_update)
    return render(request, 'news/manage/form.html', {'form_post': form_post })
           
           
           
def Author_Form(request):
    if request.user.is_authenticated:
        user = request.user
        author = Author.objects.filter(user=user)
        if author.exists():
            return redirect('manage_post_list')
        else:
            pass
        if request.method == 'POST':
            author_form = AuthorForm(request.POST)
            if author_form.is_valid():
                new_author = author_form.save(commit=False)
                new_author.user = user
                new_author = author_form.save()
                group = Group.objects.get(name='Publishers')
                group.user_set.add(user)
                messages.success(request, 'ADDED SUCCESFULLY TO THE AUTHOR GROUP')
                return redirect('manage_post_list')
            else:
                messages.error(request, 'CORRECT THE ERROR BELOW')
        else:
            author_form = AuthorForm()
        return render(request, 'news/author_form.html', {'author_form': author_form})
    else:
        return redirect('register')
                
                
def get_post_name(request):
    post_name = request.session.get('post_title', None)
    return {'post_name': post_name}
    