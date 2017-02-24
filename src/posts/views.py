from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.views import View

# Q LOOKUP
from django.db.models import Q

# TIMEZONE
from django.utils import timezone

# PAGINATOR
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# MIXINS
from django_blog.mixins import (
    MultiSlugMixin,
    LoginRequiredMixin,
    StaffRequiredMixin)

# MODEL AND FORM
from django.contrib.contenttypes.models import ContentType
from .models import Post
from .forms import PostForm
from comments.models import Comment
from comments.forms import CommentForm


class PostListView(ListView):
    template_name = "posts/index.html"
    context_object_name = "posts"

    def get_queryset(self):
        queryset_list = Post.objects.active().order_by("-updated_at")
        if self.request.user.is_staff or self.request.user.is_superuser:
            queryset_list = Post.objects.all()

        search_query = self.request.GET.get("q")
        if search_query:
            queryset_list = queryset_list.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__username__icontains=search_query)
            ).distinct()
        paginator = Paginator(queryset_list, 2)

        page = self.request.GET.get("page")
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        index = context["posts"].number - 1
        max_index = len(context["posts"].paginator.page_range)
        start_index = index - 2 if index >= 2 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        context["page_range"] = context[
            "posts"].paginator.page_range[start_index:end_index]
        context["today"] = timezone.now().date
        return context


class PostDetailView(MultiSlugMixin, DetailView):
    template_name = "posts/detail.html"
    model = Post
    pk_url_kwarg = "id"
    context_object_name = "post"

    def get_object(self, *args, **kwargs):
        user = self.request.user
        post = super(PostDetailView, self).get_object(*args, **kwargs)
        if post.pub_date:
            if post.pub_date > timezone.now().date() or post.draft:
                if not post.user == user or not user.is_staff or not user.is_superuser:
                    raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context["today"] = timezone.now().date()
        context["comments"] = Comment.objects.filter_by_instance(
            context["post"]).order_by("-updated_at")
        context["properties"] = context["post"].comments

        initial_data = {
            "content_type": context["post"].get_content_type,
            "object_id": context["post"].id,
        }
        context["comment_form"] = CommentForm(None, initial=initial_data)
        return context

    def post(self, request, slug=None):
        form = CommentForm(request.POST)
        if form.is_valid() and request.user.is_authenticated():
            content_type = ContentType.objects.get(model=form.cleaned_data.get("content_type"))
            object_id = form.cleaned_data.get("object_id")
            content = form.cleaned_data.get("content")
            parent_obj = None
            try:
                parent_id = int(request.POST.get("parent_id"))
            except:
                parent_id = None
            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    parent_obj = parent_qs.first()
            print(parent_qs)

            new_comment, created = Comment.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=object_id,
                content=content,
                parent = parent_obj
            )
            # if created:
            #     print("ok working!!")
        return redirect("posts:detail_slug", slug=slug)


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = "posts/create.html"
    model = Post
    form_class = PostForm
    context_object_name = "post"
    success_url = reverse_lazy('posts:index')

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        messages.success(self.request, "New post has been created",
                         extra_tags="alert-success")
        return super(PostCreateView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Error Occured during the posting", extra_tags="alert-danger")
        return super(PostCreateView, self).form_valid(form)


class PostUpdateView(LoginRequiredMixin, MultiSlugMixin, UpdateView):
    template_name = "posts/create.html"
    model = Post
    form_class = PostForm
    pk_url_kwarg = "id"
    context_object_name = "post"

    def get_object(self, *args, **kwargs):
        user = self.request.user
        post = super(PostUpdateView, self).get_object(*args, **kwargs)
        if not post.user == user or not user.is_staff or not user.is_superuser:
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super(PostUpdateView, self).get_context_data(**kwargs)
        context["update"] = "update"
        return context

    def form_valid(self, form_class):
        print(self.get_form_kwargs().get("files"))
        if self.request.FILES:
            image = form.cleaned_data["image"]
        messages.success(self.request, "The post has been updated",
                         extra_tags="alert-success")
        return super(PostUpdateView, self).form_valid(form_class)

    def form_invalid(self, form_class):
        messages.error(
            self.request, "Error Occured during the post updating", extra_tags="alert-danger")
        return super(PostUpdateView, self).form_valid(form_class)


class PostDeleteView(DeleteView):
    model = Post
    pk_url_kwarg = "id"
    template_name = "posts/index.html"
    success_url = reverse_lazy("posts:index")

    def get_object(self, *args, **kwargs):
        user = self.request.user
        post = super(PostDeleteView, self).get_object(*args, **kwargs)
        if not post.user == user or not user.is_staff or not user.is_superuser:
            raise Http404
        return post
