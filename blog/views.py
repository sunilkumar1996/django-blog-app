from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage,\
                                  PageNotAnInteger
from django.core.mail import send_mail
from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm
from taggit.models import Tag
from django.views.generic import View, ListView
import logging

logger = logging.getLogger(__name__)

class PostListView(ListView):
    # logger.debug('This is a debug message')
    # logger.info('This is an info message')
    # logger.warning('This is a warning message')
    # logger.error('This is an error message')
    queryset = Post.published.all()
    logger.info(f"User visited in Post list view")
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None):
    logger.info(f"User visited in Post list with tag_slug {tag_slug}")
    context = {}
    template_name = 'blog/post/list.html'
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3) # 3 posts in each page
    page = request.GET.get('page')
    context['page'] = page
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        logger.error(f"Error in post list with slug : {PageNotAnInteger}")
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        logger.error(f"Error in post list tag {EmptyPage}")
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    context['posts'] = posts
    context['tag'] = tag
    logger.info(f"post list tag successfully render to html page!")
    return render(request, template_name, context)


def post_detail(request, year, month, day, post):
    logger.info(f"User visited in post_detail method!")
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        logger.info(f"User requsted for post method in comment detail!")
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            email = comment_form.cleaned_data.get('email')
            logger.info(f"Comment form is valid in post_detail for {email}")
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
            logger.info(f"comment successfully saved for {email}")
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                .order_by('-same_tags','-publish')[:4]
    logger.info(f"post list tag successfully render to html page!")
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts})


class PostShareView(View):
    template_name = "blog/post/share.html"

    def get(self, request, post_id):
        logger.info(f"User visted in PostShareView!")
        context = {}
        context['post'] = get_object_or_404(Post, id=post_id, status='published')
        context['form'] = EmailPostForm()
        return render(request, self.template_name, context)
    
    def post(self, request, post_id):
        context = {}
        sent = False
        logger.info(f"User submitted the form for share the Post")
        post = get_object_or_404(Post, id=post_id, status='published')
        context['post'] = post
        form = EmailPostForm(request.POST)
        context['form'] = form
        if form.is_valid():
            logger.info(f"form is valid in share the post view")
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'sunilrajput.dev@gmail.com', [cd['to']])
            sent = True
            logger.info(f"Blog post shared successfully")
        context['sent'] = sent
        logger.info(f"Email status: {sent} and redner to html in Postshare view!")
        return render(request, self.template_name, context)


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')
    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})
