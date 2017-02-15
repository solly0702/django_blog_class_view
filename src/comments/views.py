from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.

# MESSAGES
from django.contrib import messages

# MODEL
from django.contrib.contenttypes.models import ContentType
from .models import Comment

# FORM
from .forms import CommentForm


def comment_thread(request, id):
    comment = get_object_or_404(Comment, id=id)
    initial_data = {
        "content_type": comment.content_type,
        "object_id": comment.object_id,
    }
    form = CommentForm(request.POST or None, initial=initial_data)
    # print(form.errors)
    if form.is_valid():
        content_type = ContentType.objects.get(
            model=form.cleaned_data.get("content_type"))
        obj_id = form.cleaned_data.get("object_id")
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

        new_comment, created = Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
            content=content,
            parent=parent_obj
        )
        return redirect(new_comment.content_object.get_absolute_url())
    context = {
        "comment": comment,
        "comment_form": form
    }
    return render(request, "comments/thread.html", context)
