# MVC => MODEL, VIEW, CONTROLER
from django.db import models
from django.utils.text import slugify

# DJANGO SIGNAL
from django.db.models.signals import pre_save, post_save

# DJANGO FIELD TYPE
from django.core.urlresolvers import reverse

# TIMEZONE
from django.utils import timezone

# DJANGO MODELS
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from comments.models import Comment

# THRID PARTY
from django.utils.safestring import mark_safe
from markdown_deux import markdown

# HELPER
from helper.read_time import get_read_time


class PostManager(models.Manager):

    def active(self, *args, **kwargs):
        return super(PostManager, self).filter(draft=False).filter(pub_date__lte=timezone.now())


def upload_location(instance, filename):
    return "%s/%s" % (instance.id, filename)


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, null=True, blank=True)
    image = models.ImageField(upload_to=upload_location,
                              null=True,
                              blank=True,
                              width_field="width_field",
                              height_field="height_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    content = models.TextField()
    draft = models.BooleanField(default=False)
    pub_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    read_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    objects = PostManager()

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse("posts:detail_slug", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["-created_at", "-updated_at"]

    def get_markdown(self):
        content = self.content
        return mark_safe(markdown(content))

    @property
    def comments(self):
        instance = self
        return Comment.objects.filter_by_instance(instance)

    @property
    def get_content_type(self):
        instance = self
        return ContentType.objects.get_for_model(instance.__class__)


def post_save_reciever(sender, instance, *args, **kwargs):
    if kwargs["created"]:
        slug = slugify(instance.title + "-" + str(instance.id))
        instance.slug = slug
        instance.save()

post_save.connect(post_save_reciever, sender=Post)

# def create_slug(instance, new_slug=None):
#     slug = slugify(instance.title)
#     if new_slug is not None:
#         slug = new_slug
#     qs = Post.objects.filter(slug=slug).order_by("-id")
#     exists = qs.exists()
#     if exists:
#         new_slug = "%s-%s" % (slug, qs.first().id)
#         return create_slug(instance, new_slug=new_slug)
#     return slug
#
#
def pre_save_reciever(sender, instance, *args, **kwargs):
    # if not instance.slug:
    #     instance.slug = create_slug(instance)
    if instance.content:
        html_string = instance.get_markdown()
        read_time = get_read_time(html_string)
        instance.read_time = read_time

pre_save.connect(pre_save_reciever, sender=Post)
