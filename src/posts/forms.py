# PAGEDOWN
from pagedown.widgets import PagedownWidget

from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    # content = forms.CharField(widget=PagedownWidget(attrs={"class": "form-control"}))

    class Meta:
        model = Post
        fields = ["title", "image", "content", "draft", "pub_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "content": PagedownWidget(show_preview=False, attrs={"class": "form-control"}),
            "draft": forms.CheckboxInput(attrs={"class": "form-control", "type": "checkbox"}),
            "pub_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def clean(self, *args, **kwargs):
        return super(PostForm, self).clean(*args, **kwargs)
