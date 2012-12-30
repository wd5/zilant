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