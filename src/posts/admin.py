from django.contrib import admin

# Register your models here.
# MODELADMIN OPTIONS

from .models import Post

class PostModelAdmin(admin.ModelAdmin):
    list_display = ["title", "created_at", "updated_at"]
    list_display_links = ["updated_at"]
    list_editable = ["title"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["title", "content"]



    class Meta:
        model = Post

admin.site.register(Post, PostModelAdmin)
