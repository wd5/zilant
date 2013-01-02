# -*- coding: utf-8 -*-
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.mail import send_mail

from yafotki.fields import YFField
from BeautifulSoup import BeautifulSoup, Comment as HtmlComment


def sanitizeHTML(value, mode='none'):
    """ Удаляет из value html-теги.
        Если mode==none - все теги
        Если mode==strict - все теги кроме разрешенных
    """
    if mode == 'strict':
        valid_tags = 'ol ul li p i strong b u a h1 h2 h3 pre br div span img blockquote glader youtube cut blue object param embed iframe'.split()
    else:
        valid_tags = []
    valid_attrs = 'href src pic user page class text title alt'.split()
    # параметры видеороликов
    valid_attrs += 'width height classid codebase id name value flashvars allowfullscreen allowscriptaccess quality src type bgcolor base seamlesstabbing swLiveConnect pluginspage data frameborder'.split()

    soup = BeautifulSoup(value)
    for comment in soup.findAll(
        text=lambda text: isinstance(text, HtmlComment)):
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in valid_tags:
            tag.hidden = True
        tag.attrs = [(attr, val) for attr, val in tag.attrs
                                 if attr in valid_attrs]
    result = soup.renderContents().decode('utf8')
    return result


class Profile(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Пользователь', null=True, blank=True, related_name='user')
    family = models.CharField(max_length=200, verbose_name=u"Фамилия", null=True, blank=True, default=None)
    name = models.CharField(max_length=200, verbose_name=u"Имя", null=True, blank=True, default=None)
    patronymic = models.CharField(max_length=200, verbose_name=u"Отчество", null=True, blank=True, default=None)
    nick = models.CharField(max_length=200, verbose_name=u"Ник", null=True, blank=True, default=None)
    club = models.CharField(max_length=200, verbose_name=u"Клуб", null=True, blank=True, default=None)
    birth = models.DateField(verbose_name=u"Дата рождения", null=True, blank=True, default=None)

    country = models.CharField(max_length=200, verbose_name=u"Страна", null=True, blank=True, default=None)
    region = models.CharField(max_length=200, verbose_name=u"Область", null=True, blank=True, default=None)
    city = models.CharField(max_length=200, verbose_name=u"Город", null=True, blank=True, default=None)
    address = models.CharField(max_length=200, verbose_name=u"Адрес", null=True, blank=True, default=None)

    passport_number = models.CharField(max_length=200, verbose_name=u"Номер паспорта", null=True, blank=True, default=None)
    passport_date = models.CharField(max_length=200, verbose_name=u"Дата выдачи", null=True, blank=True, default=None)
    passport_given = models.CharField(max_length=200, verbose_name=u"Кем выдан", null=True, blank=True, default=None)

    med_doc = models.CharField(max_length=200, verbose_name=u"Номер полиса", null=True, blank=True, default=None)
    health = models.CharField(max_length=200, verbose_name=u"Состояние здоровья", null=True, blank=True, default=None)
    health_add = models.TextField(verbose_name=u"Состояние здоровья", null=True, blank=True, default=None)

    icq = models.CharField(max_length=200, verbose_name=u"ICQ", null=True, blank=True, default=None)
    tel = models.CharField(max_length=200, verbose_name=u"Телефон", null=True, blank=True, default=None)
    skype = models.CharField(max_length=200, verbose_name=u"Skype", null=True, blank=True, default=None)

    photo = YFField(verbose_name=u"Фото", upload_to='zilant', null=True, blank=True, default=None)

    parent_profile = models.ForeignKey('self', verbose_name=u'Заявка ответственного', null=True, blank=True, default=None, related_name='parent')

    def __unicode__(self):
        return self.name or ""

    def user_email(self):
        return self.user.email
    user_email.short_description = u"Email"

    def user_username(self):
        return self.user.username
    user_username.short_description = u"Ник"

    def save(self, check_diff=True, *args, **kwargs):
        if check_diff:
            report = ""
            if self.pk:
                prev = self.__class__.objects.get(pk=self.pk)
                report = u"Измененные поля профиля [%s]:\n" % self.user.pk
                for field in self._meta.fields:
                    if field.name in('paid', 'locked_fields'):
                        continue

                    if getattr(self, field.name) != getattr(prev, field.name):
                        report += u"%s: '%s' -> '%s'\n" % (field.verbose_name, getattr(prev, field.name) or '-', getattr(self, field.name) or '-')
            else:
                report = u"Новый посетитель [%s]:\n" % self.user.pk
                for field in self._meta.fields:
                    if field.name in('paid', 'locked_fields'):
                        continue
                    report += u"%s: '%s'\n" % (field.verbose_name, getattr(self, field.name) or '-')

            if report:
                emails = [self.user.email]

                send_mail(
                    u"Зилант: профиль посетителя %s" % self.name,
                    report,
                    None,
                    emails,
                )

        return super(Profile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Заявка"
        verbose_name_plural = u"Заявки"
