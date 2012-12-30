# -*- coding: utf-8 -*-
from django.conf.urls import *
from django.views.generic import list_detail

from .models import Article

urlpatterns = patterns('',
    url(r'^/(?P<object_id>\d+)$', list_detail.object_detail, {'queryset': Article.objects.all()}, name='article'),
    url(r'^/(?P<slug>\w+)$', list_detail.object_detail, {'queryset': Article.objects.all()}, name='article'),
)