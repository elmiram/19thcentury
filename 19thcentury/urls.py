from django.conf.urls import patterns, include, url
from django.contrib import admin
from TestCorpus.views import Index, Search, Statistics, PopUp
from news.views import NewsView
from annotator.admin import learner_admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'learner_corpus.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^myadmin/', include(learner_admin.urls)),

    url(r'^admin/', include(learner_admin.urls)),
    url(r'^(|index2|help|start|publications|authors|texts|annotation|team)$', Index.as_view(), name='main.static'),
    url(r'^(news)$', NewsView.as_view(), name='news'),
    url(r'^(search)/$', Search.as_view(), name='main.search'),
    url(r'^search/(gramsel|lex|errsel)$', PopUp.as_view(), name='popup'),
    url(r'^(stats)/$', Statistics.as_view(), name='main.stats'),
    url(r'^document-annotations', include('annotator.urls')),
    )
