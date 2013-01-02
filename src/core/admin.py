# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import *



class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'name', 'user_username', 'user_email',
        'tel', 'city'
    )
    list_per_page = 300

    def lookup_allowed(self, *args, **kwargs):
        return True


admin.site.register(Profile, ProfileAdmin)

admin.site.register(EventPlace)
admin.site.register(EventType)
admin.site.register(EventBlock)
admin.site.register(Event)
