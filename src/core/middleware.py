# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from .models import Profile

class Prepare:
    def process_request(self, request):
        request.profile = None
        request.role = None

        request.actual_user = request.user
        request.actual_profile = None

        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=request.user)
            request.actual_profile = request.profile = profile
