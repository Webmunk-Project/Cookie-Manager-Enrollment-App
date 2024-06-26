# -*- coding: utf-8 -*-
# pylint: disable=no-member,line-too-long

from django.core.management.base import BaseCommand

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments

from ...models import ScheduledTask

class Command(BaseCommand):
    help = 'Checks outstanding tasks for completion'

    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_lock
    @handle_schedule
    def handle(self, *args, **options):
        for task in ScheduledTask.objects.filter(completed=None):
            task.is_complete()
