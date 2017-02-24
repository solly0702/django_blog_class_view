from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.

# MESSAGES
from django.contrib import messages

# MODEL
from django.contrib.contenttypes.models import ContentType
from .models import Comment

# FORM
from .forms import CommentForm

@login_required(login_url="accounts:login") # settings.py => LOGIN_URL = '/login/'
def comment_delete(request, id):
    try:
        comment = Comment.objects.get(id=id)
    except:
        raise Http404

    if comment.user != request.user:
        messages.success(request, "You do not have permission to do this action.", extra_tags="alert-danger")
        return redirect("comments:thread", id=id)

        ## CUSTOM HTTP REQUEST
        # res = HttpResponse("You do not have permissiont for this action")
        # res.status_code = 403
        # return res
        # return render(request, "403.html", context, status_code=403)

    if request.method == "POST":
        parent_url = comment.content_object.get_absolute_url()
        comment.delete()
        messages.success(request, "Successfully deleted.",
                         extra_tags="alert-success")
        return redirect(parent_url)
    context = {
        "comment": comment
    }
    return render(request, "comments/delete.html", context)


def comment_thread(request, id):
    try:
        comment = Comment.objects.get(id=id)
    except:
        raise Http404

    if not comment.is_parent:
        comment = comment.parent

    initial_data = {
        "content_type": comment.content_type,
        "object_id": comment.object_id,
    }
    form = CommentForm(request.POST or None, initial=initial_data)
    # print(form.errors)
    if form.is_valid() and request.user.is_authenticated:
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
