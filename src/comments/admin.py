from django.contrib import admin

# Register your models here.
from .models import Comment


class CommentModelAdmin(admin.ModelAdmin):
    list_display = ["user", "content","created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user", "content"]

    class Meta:
        model = Comment

admin.site.register(Comment, CommentModelAdmin)
