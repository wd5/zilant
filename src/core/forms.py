# -*- coding: utf-8 -*-
import re
from datetime import date

from django.contrib.auth import authenticate
from django.forms import *
from django.db.models import Q

from .models import *


class CommonForm(Form):
    def errors_list(self):
        return [u"%s: %s" % (self.fields[_].label, message) for _, l in self.errors.items() for message in l]

    def str_errors(self, divider=u" "):
        return divider.join(self.errors_list())


class RegistrationForm(CommonForm):
    email = EmailField(label=u'Email', max_length=100)
    passwd = CharField(label=u'Пароль', max_length=100, widget=PasswordInput)
    passwd2 = CharField(label=u'Пароль еще раз', max_length=100, widget=PasswordInput)

    def clean(self):
        if self.cleaned_data.get('passwd') != self.cleaned_data.get('passwd2'):
            raise ValidationError(u"Пароли должны быть одинаковыми.")

        return self.cleaned_data

    def save(self):
        new_user = User.objects.create_user(
            self.cleaned_data['email'],
            self.cleaned_data['email'],
            self.cleaned_data['passwd']
        )
        new_user.is_active = True
        new_user.save()

        return authenticate(username=new_user.username, password=self.cleaned_data['passwd'])


class LoginForm(CommonForm):
    login = CharField(label=u'Ник', max_length=100)
    passwd = CharField(label=u'Пароль', max_length=100, widget=PasswordInput)
    retpath = CharField(max_length=2000, required=False, widget=HiddenInput)

    def get_user(self, s):
        u""" Проверяет строку на емейл, логин или номер пользователя """
        if s.isdigit():
            return User.objects.get(id=s)
        else:
            return User.objects.get(Q(username=s) | Q(email=s))

    def clean(self):
        login = self.cleaned_data.get('login', '')
        passwd = self.cleaned_data.get('passwd', '')

        try:
            user = self.get_user(login)
        except User.DoesNotExist:
            raise ValidationError(u'Логин или пароль не верен')

        auth_user = authenticate(username=user.username, password=passwd)
        if auth_user:
            self.user = auth_user
            return self.cleaned_data
        else:
            raise ValidationError(u'Логин или пароль не верен')


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']

    family = CharField(max_length=200, label=u"Фамилия")
    name = CharField(max_length=200, label=u"Имя")
    patronymic = CharField(max_length=200, label=u"Отчество")
    birth = DateField(label=u"Дата рождения", help_text=u"В виде ГГГГ-ММ-ДД")
    country = CharField(max_length=200, label=u"Страна")
    region = CharField(max_length=200, label=u"Область")
    city = CharField(max_length=200, label=u"Город")
    passport_number = CharField(max_length=200, label=u"Номер паспорта")
    passport_date = DateField(label=u"Дата выдачи", help_text=u"В виде ГГГГ-ММ-ДД")
    passport_given = CharField(max_length=200, label=u"Кем выдан")
    med_doc = CharField(max_length=200, label=u"Номер полиса")
    health = CharField(max_length=200, label=u"Состояние здоровья")

    def clean(self):
        if self.cleaned_data.get('birth'):
            age = (date.today() - self.cleaned_data.get('birth')).days / 365

            if age >= 18 and not self.cleaned_data.get('photo'):
                raise ValidationError(u"Пожалуйста приложите свою фотографию")

            if age < 18 and not self.cleaned_data.get('parent_profile'):
                raise ValidationError(u"Пожалуйста укажите ответственного за вас")

        return self.cleaned_data


class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = ['author']

    def save(self, user, *args, **kwargs):
        event = super(EventForm, self).save(commit=False)

        event.author = user
        event.save()
        return event