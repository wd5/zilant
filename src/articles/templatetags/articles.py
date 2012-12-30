# encoding: utf-8

from django import template
from ..models import Article

register = template.Library()


@register.simple_tag()
def content(article_id):
    if article_id.isdigit():
        return Article.objects.get(pk=article_id).content
    else:
        return Article.objects.get(slug=article_id).content


@register.inclusion_tag("articles/article_list.html")
def children(article_id):
    if article_id.isdigit():
        parent = Article.objects.get(pk=article_id)
    else:
        parent = Article.objects.get(slug=article_id)

    return {'articles': Article.objects.filter(parent=parent)}