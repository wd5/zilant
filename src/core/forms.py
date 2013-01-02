# -*- coding: utf-8 -*-
from datetime import date

from django.contrib.auth import authenticate
from django import forms
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Profile, Event, EventPrint


class CommonForm(forms.Form):
    def errors_list(self):
        return [u"%s: %s" % (self.fields[_].label, message) for _, l in self.errors.items() for message in l]

    def str_errors(self, divider=u" "):
        return divider.join(self.errors_list())


class RegistrationForm(CommonForm):
    email = forms.EmailField(label=u'Email', max_length=100)
    passwd = forms.CharField(label=u'Пароль', max_length=100, widget=forms.PasswordInput)
    passwd2 = forms.CharField(label=u'Пароль еще раз', max_length=100, widget=forms.PasswordInput)

    def clean(self):
        if self.cleaned_data.get('passwd') != self.cleaned_data.get('passwd2'):
            raise forms.ValidationError(u"Пароли должны быть одинаковыми.")

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
    login = forms.CharField(label=u'Ник', max_length=100)
    passwd = forms.CharField(label=u'Пароль', max_length=100, widget=forms.PasswordInput)
    retpath = forms.CharField(max_length=2000, required=False, widget=forms.HiddenInput)

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
            raise forms.ValidationError(u'Логин или пароль не верен')

        auth_user = authenticate(username=user.username, password=passwd)
        if auth_user:
            self.user = auth_user
            return self.cleaned_data
        else:
            raise forms.ValidationError(u'Логин или пароль не верен')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']

    family = forms.CharField(max_length=200, label=u"Фамилия")
    name = forms.CharField(max_length=200, label=u"Имя")
    patronymic = forms.CharField(max_length=200, label=u"Отчество")
    birth = forms.DateField(label=u"Дата рождения", help_text=u"В виде ГГГГ-ММ-ДД")
    country = forms.CharField(max_length=200, label=u"Страна")
    region = forms.CharField(max_length=200, label=u"Область")
    city = forms.CharField(max_length=200, label=u"Город")
    passport_number = forms.CharField(max_length=200, label=u"Номер паспорта")
    passport_date = forms.DateField(label=u"Дата выдачи", help_text=u"В виде ГГГГ-ММ-ДД")
    passport_given = forms.CharField(max_length=200, label=u"Кем выдан")
    med_doc = forms.CharField(max_length=200, label=u"Номер полиса")
    health = forms.CharField(max_length=200, label=u"Состояние здоровья")

    def clean(self):
        if self.cleaned_data.get('birth'):
            age = (date.today() - self.cleaned_data.get('birth')).days / 365

            if age >= 18 and not self.cleaned_data.get('photo'):
                raise forms.ValidationError(u"Пожалуйста приложите свою фотографию")

            if age < 18 and not self.cleaned_data.get('parent_profile'):
                raise forms.ValidationError(u"Пожалуйста укажите ответственного за вас")

        return self.cleaned_data


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['author']

    def save(self, user, *args, **kwargs):
        event = super(EventForm, self).save(commit=False)

        event.author = user
        event.save()
        return event


PrintFormSet = forms.models.inlineformset_factory(Event, EventPrint, fk_name="event", can_delete=False, extra=1)