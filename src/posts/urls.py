from django.conf.urls import url
from . import views

app_name = 'posts'

urlpatterns = [
    url(r'^$', views.PostListView.as_view(), name="index"),
    url(r'^create/$', views.PostCreateView.as_view(), name="create"),
    url(r'^(?P<id>\d+)/$', views.PostDetailView.as_view(), name="detail"),
    url(r'^(?P<slug>[\w-]+)/$', views.PostDetailView.as_view(), name="detail_slug"),
    url(r'^(?P<id>\d+)/update/$', views.PostUpdateView.as_view(), name="update"),
    url(r'^(?P<slug>[\w-]+)/update/$', views.PostUpdateView.as_view(), name="update_slug"),
    url(r'^(?P<id>\d+)/delete/$', views.PostDeleteView.as_view(), name="delete"),
]
