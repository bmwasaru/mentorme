from django.conf.urls import url
from django.views.decorators.cache import cache_page

from questions import views

urlpatterns = [
    url(r'^$', views.questions, name='questions'),
    url(r'^answered/$', cache_page(60 * 15)(views.answered), name='answered'),
    url(r'^unanswered/$', cache_page(60 * 15)(views.unanswered), name='unanswered'),
    url(r'^all/$', cache_page(60 * 15)(views.all), name='all'),
    url(r'^ask/$', cache_page(60 * 15)(views.ask), name='ask'),
    url(r'^favorite/$', views.favorite, name='favorite'),
    url(r'^answer/$', views.answer, name='answer'),
    url(r'^answer/accept/$', views.accept, name='accept'),
    url(r'^answer/vote/$', views.vote, name='vote'),
    url(r'^(\d+)/$', cache_page(60 * 60)(views.question), name='question'),
    url(r'^category/(?P<category>[\w@.-]+)/$', cache_page(60 * 15)(views.category), name='category'),
    url(r'^tag/(?P<tag>[\w@.-]+)/$', cache_page(60 * 15)(views.tag), name='tag'),
]
