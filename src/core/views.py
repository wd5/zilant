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
    if request.POST:
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)

            role_form = ChooseRoleForm(request.POST)
            if role_form.is_valid():
                profile = user.get_profile()
                profile.role = role_form.cleaned_data['role']
                profile.save()
                return HttpResponseRedirect(reverse('form') + '?save=ok')

            return HttpResponseRedirect("/")

    else:
        form = RegistrationForm()

    return render_to_response(
        request,
        'registration.html',
        {
            'form': form,
            'role': request.GET.get('role', '') or request.POST.get('role', ''),
        }
    )


def lock_role(request, user_id):
    if not request.user.is_superuser:
        raise Http404()

    profile = User.objects.get(pk=user_id).get_profile()
    if not profile.role:
        return HttpResponseRedirect('/admin/core/profile/')

    role = profile.role
    if role.profile == profile:
        role.profile = None
        role.save()

    else:
        Profile.objects.filter(role=role).exclude(pk=profile.pk).update(role=None)
        role.profile = profile
        role.save()

    return HttpResponseRedirect('/admin/core/profile/')


@login_required
def form(request):
    if request.POST:
        if request.actual_profile.role:
            valid = True
            forms = {
                'form': RoleForm(request.POST, request.FILES, instance=request.actual_profile.role),
                'quest_form': QuestForm(request.POST, instance=request.actual_profile.role),
                'connections_formset': ConnectionFormSet(request.POST, instance=request.actual_profile.role),
                'markers_formset': MarkersFormSet(request.POST, instance=request.actual_profile.role),
            }
            for name, form in forms.items():
                if form.is_valid():
                    form.save()
                else:
                    valid = False

            if valid:
                request.actual_profile.role.correct_markers()
                return HttpResponseRedirect(reverse('form') + '?save=ok&change_user=%s' % request.actual_user.pk)

            return render_to_response(request, 'form.html', forms)

    else:
        if request.actual_profile.role:
            forms = {
                'form': RoleForm(instance=request.actual_profile.role),
                'quest_form': QuestForm(instance=request.actual_profile.role),
                'connections_formset': ConnectionFormSet(instance=request.actual_profile.role),
                'markers_formset': MarkersFormSet(instance=request.actual_profile.role),
            }
            return render_to_response(request, 'form.html', forms)

    free_roles = Role.objects.filter(profile__isnull=True)
    if free_roles:
        form = ChooseRoleForm()
        return render_to_response(request, 'choose_role.html', {'form': form})
    else:
        return add_role(request)


@login_required
def choose_role(request):
    if request.actual_role:
        # За пользователем уже закреплена роль
        return HttpResponseRedirect("/")

    if request.POST:
        form = ChooseRoleForm(request.POST)
        if form.is_valid():
            request.actual_profile.role = form.cleaned_data['role']
            request.actual_profile.save()
            return HttpResponseRedirect(reverse('form') + '?save=ok&change_user=%s' % request.actual_user.pk)

    else:
        form = ChooseRoleForm()

    return render_to_response(request, 'choose_role.html', {'form': form})


@login_required
def add_role(request):
    if request.actual_role:
        # За пользователем уже закреплена роль
        return HttpResponseRedirect("/")

    if request.POST:
        form = RoleForm(request.POST, request.FILES)
        if form.is_valid():
            role = form.save()
            request.actual_profile.role = role
            request.actual_profile.save()
            return HttpResponseRedirect(reverse('form') + '?save=ok&change_user=%s' % request.actual_user.pk)

    else:
        form = RoleForm()

    return render_to_response(request, 'add_role.html', {'form': form})


def roles(request):
    traditions = [(tradition.code, tradition.name) for tradition in Tradition.objects.all()]
    current_tradition = request.GET.get('location', 'red')
    roles = Role.objects.filter(tradition__code=current_tradition).order_by('tradition', 'name')

    return render_to_response(request, 'roles.html', {
        'roles': roles,
        'locations': traditions,
        'current_location': current_tradition,
    })


@login_required
def profile(request):
    if request.POST:
        form = ProfileForm(request.POST, request.FILES, instance=request.actual_profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('profile') + '?save=ok&change_user=%s' % request.actual_user.pk)
    else:
        form = ProfileForm(instance=request.actual_profile)

    return render_to_response(request, 'profile.html', {'form': form})


def tradition_view(request, code):
    tradition = Tradition.objects.get(code=code)

    if request.POST and request.POST.get('post'):
        TraditionGuestbook.objects.create(
            tradition=tradition,
            author=request.actual_user,
            content=request.POST.get('post'),
        )
        recievers = [role.profile.user.email for role in Role.objects.filter(tradition=tradition, profile__isnull=False)]
        email(
            u"Зазеркалье: Новая запись",
            u"Новая запись на странице '%s'. http://%s%s" % (tradition.name, settings.DOMAIN, reverse('tradition', args=[tradition.code])),
            recievers,
        )
        return HttpResponseRedirect(reverse('tradition', args=[tradition.code]) + '?save=ok')

    context = {
        'tradition': tradition,
        'articles': tradition.traditiontext_set.all(),
        'files': tradition.traditionfile_set.all(),
        'url': reverse('tradition', args=[tradition.code]),
        'has_access': tradition in request.companies,
    }

    context.update(make_pages(tradition.traditionguestbook_set.all().order_by('-dt_created'),
        20,
        request.GET.get('page')
    ))

    return render_to_response(request, 'tradition.html', context)


def add_tradition_text(request, code):
    tradition = Tradition.objects.get(code=code)
    if request.POST:
        form = TraditionTextForm(request.POST)
        if form.is_valid():
            TraditionText.objects.create(
                tradition=tradition,
                author=request.actual_user,
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
            )
            return HttpResponseRedirect(reverse('tradition', args=[tradition.code]) + '?save=ok')
    else:
        form = TraditionTextForm()

    return render_to_response(request, 'add_tradition_text.html', {'form': form})


def add_tradition_file(request, code):
    tradition = Tradition.objects.get(code=code)
    if request.POST:
        form = TraditionFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.author = request.user
            file.tradition = tradition
            file.save()
            return HttpResponseRedirect(reverse('tradition', args=[tradition.code]) + '?save=ok')
    else:
        form = TraditionFileForm()

    return render_to_response(request, 'add_tradition_file.html', {'form': form})


def tradition_text(request, code, number):
    tradition = Tradition.objects.get(code=code)
    text = get_object_or_404(TraditionText, tradition=tradition, pk=number)
    return render_to_response(request, 'tradition_text.html', {'text': text})


def edit_tradition_text(request, code, number):
    tradition = Tradition.objects.get(code=code)
    text = get_object_or_404(TraditionText, tradition=tradition, pk=number)
    if request.POST:
        form = TraditionTextModelForm(request.POST, instance=text)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('tradition_text', args=[tradition.code, text.id]) + '?save=ok')
    else:
        form = TraditionTextModelForm(instance=text)

    return render_to_response(request, 'edit_tradition_text.html', {'form': form})