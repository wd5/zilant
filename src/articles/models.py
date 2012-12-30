# -*- coding: utf-8 -*-
from django.db import models


class Article(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, default=None)
    title = models.CharField(verbose_name=u"Заголовок", max_length=50)
    slug = models.CharField(verbose_name=u"Имя для урла", max_length=50, null=True, blank=True, default=None)
    content = models.TextField(verbose_name=u"Содержание")
    order = models.PositiveSmallIntegerField(verbose_name=u"Порядок", default=100)
    redirect = models.CharField(verbose_name=u"Редирект", max_length=50, null=True, blank=True, default=None)
    path = models.CharField(verbose_name=u"Путь", max_length=50, default="", blank=True)

    def __unicode__(self): return self.title

    def save(self, *args, **kwargs):
        if not self.path:
            if self.parent:
                above_amount = Article.objects.filter(parent=self.parent).count()
                self.path = self.parent.path + "%02d" % (above_amount + 1)
            else:
                above_amount = Article.objects.filter(parent__isnull=True).count()
                self.path = "%02d" % (above_amount + 1)

        super(Article, self).save(*args, **kwargs)

    def indent_title(self):
        return u'&nbsp' * len(self.path) + self.title
    indent_title.short_description = u"Название"
    indent_title.allow_tags = True

    class Meta:
        verbose_name = u"Страница"
        verbose_name_plural = u"Страницы"
        ordering = ('order',)
