from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404


class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class StaffRequiredMixin(object):

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


class MultiSlugMixin(object):
    model = None

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        modelClass = self.model
        if slug is not None:
            try:
                obj = get_object_or_404(modelClass, slug=slug)
            except modelClass.MultipleObjectsReturned:
                obj = Post.objects.filter(slug=slug).order_by("-title").first()
        else:
            obj = super(MultiSlugMixin, self).get_object(*args, **kwargs)
        return obj
