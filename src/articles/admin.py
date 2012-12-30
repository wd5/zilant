# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import *

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('indent_title', 'slug', 'order', 'path')
    actions = ['recalc_paths']
    ordering = ('path',)

    def recalc_paths(self, request, queryset):
        for number, article in enumerate(Article.objects.filter(parent__isnull=True).order_by('order')):
            article.path = "%02d" % (number + 1)
            article.save()

            self._recalc_article_children(article)
    recalc_paths.short_description = u"Пересчитать порядок"

    def _recalc_article_children(self, article):
        for number, child in enumerate(Article.objects.filter(parent=article).order_by('order')):
            child.path = article.path + "%02d" % (number + 1)
            child.save()
            self._recalc_article_children(child)

admin.site.register(Article, ArticleAdmin)
