from django.urls import re_path

from articles import views

urlpatterns = [
    re_path(r'^$', views.articles, name='articles'),
    re_path(r'^write/$', views.CreateArticle.as_view(), name='write'),
    re_path(r'^preview/$', views.preview, name='preview'),
    re_path(r'^drafts/$', views.drafts, name='drafts'),
    re_path(r'^comment/$', views.comment, name='comment'),
    re_path(r'^tag/(?P<tag_name>.+)/$', views.tag, name='tag'),
    re_path(r'^edit/(?P<pk>\d+)/$',
        views.EditArticle.as_view(), name='edit_article'),
    re_path(r'^(?P<slug>[-\w]+)/$', views.article, name='article'),
]
