# pylint: disable=no-member, line-too-long

from django.contrib.gis import admin

from .models import Enrollment, EnrollmentGroup, ExtensionRuleSet, ScheduledTask

@admin.register(Enrollment)
class EnrollmentAdmin(admin.OSMGeoAdmin):
    list_display = ('assigned_identifier', 'group', 'enrolled', 'rule_set', 'last_fetched')
    list_filter = ('group', 'enrolled', 'last_fetched', 'rule_set', )

    search_fields = ('assigned_identifier',)

@admin.register(EnrollmentGroup)
class EnrollmentGroupAdmin(admin.OSMGeoAdmin):
    list_display = ('name',)

    search_fields = ('name',)

@admin.register(ExtensionRuleSet)
class ExtensionRuleSetAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'is_active', 'is_default',)
    list_filter = ('is_active', 'is_default',)

    search_fields = ('name', 'rule_json')

def reset_scheduled_task_completions(modeladmin, request, queryset): # pylint: disable=unused-argument, invalid-name
    queryset.update(completed=None)

reset_scheduled_task_completions.description = 'Reset scheduled task completions'

@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.OSMGeoAdmin):
    list_display = ('enrollment', 'slug', 'task', 'active', 'last_check', 'completed')
    list_filter = ('active', 'completed', 'last_check', 'slug',)

    search_fields = ('task', 'slug', 'url',)
    actions = [reset_scheduled_task_completions]
