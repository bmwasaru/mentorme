from django.urls import re_path
from django.views.decorators.cache import cache_page

from questions import views

urlpatterns = [
    re_path(r'^$', views.questions, name='questions'),
    re_path(r'^answered/$', views.answered, name='answered'),
    re_path(r'^unanswered/$', views.unanswered, name='unanswered'),
    re_path(r'^all/$', views.all, name='all'),
    re_path(r'^ask/$', views.ask, name='ask'),
    re_path(r'^favorite/$', views.favorite, name='favorite'),
    re_path(r'^answer/$', views.answer, name='answer'),
    re_path(r'^answer/accept/$', views.accept, name='accept'),
    re_path(r'^answer/vote/$', views.vote, name='vote'),
    re_path(r'^(\d+)/$', views.question, name='question'),
    re_path(r'^category/(?P<category>[\w@.-]+)/$', views.category, name='category'),
    re_path(r'^tag/(?P<tag>[\w@.-]+)/$', views.tag, name='tag'),
]
