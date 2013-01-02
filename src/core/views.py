# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import random

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from .forms import *
from .utils import render_to_response, make_pages


def registration(request):
    if request.GET.get('save'):
        return render_to_response(request, 'registration.html', {'message': u"Ваша заявка успешно сохранена"})

    context = {}

    if request.POST:
        profile = None
        if request.user.is_authenticated():
            profile = request.user.get_profile()

        else:
            context['registration_form'] = RegistrationForm(request.POST)
            if context['registration_form'].is_valid():
                # Вдруг он уже зареган
                login_form = LoginForm(request.POST)
                if login_form.is_valid():
                    request.user = login_form.user
                    profile = request.user.get_profile()
                    auth.login(request, request.user)
                    del context['registration_form']

                else:
                    try:
                        login_form.get_user(request.POST.get('email'))
                        context['message'] = u"Вы ввели неправильный пароль к своей учетной записи."
                    except User.DoesNotExist:
                        # Заводим нового пользователя
                        request.user = context['registration_form'].save()
                        profile = Profile.objects.create(user=request.user)
                        auth.login(request, request.user)
                        del context['registration_form']

        if profile:
            # Юзер залогинен, можно обрабатывать заявку
            context['profile_form'] = ProfileForm(request.POST, request.FILES, instance=profile)
            if context['profile_form'].is_valid():
                context['profile_form'].save()
                return HttpResponseRedirect(reverse('registration') + '?save=ok')
        else:
            context['profile_form'] = ProfileForm(request.POST)

    else:
        context['registration_form'] = RegistrationForm()
        context['profile_form'] = ProfileForm()

    return render_to_response(request, 'registration.html', context)


@login_required
def profile(request):
    if request.GET.get('save'):
        return render_to_response(request, 'profile.html', {'message': u"Ваша заявка успешно сохранена"})

    if request.POST:
        form = ProfileForm(request.POST, request.FILES, instance=request.actual_profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('profile') + '?save=ok')
    else:
        form = ProfileForm(instance=request.actual_profile)

    return render_to_response(request, 'profile.html', {'profile_form': form})


@login_required
def add_event(request):
    if request.POST:
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(request.user)
            return HttpResponseRedirect(reverse('event', args=[event.id]))
    else:
        form = EventForm()

    return render_to_response(request, 'add_event.html', {'form': form})


def event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render_to_response(request, 'event.html', {'event': event})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.POST:
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save(request.user)
    else:
        form = EventForm(instance=event)

    return render_to_response(request, 'edit_event.html', {'form': form})