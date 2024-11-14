from django.contrib import admin

from groups.models import GroupNames


@admin.register(GroupNames)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ['name', 'chat']
