# pylint: disable=line-too-long, no-member

import datetime
import json

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Enrollment, EnrollmentGroup, ExtensionRuleSet

@csrf_exempt
def enroll(request): # pylint: disable=too-many-branches
    raw_identifier = request.POST.get('identifier', request.GET.get('identifier', None))

    payload = {}

    now = timezone.now()

    if raw_identifier is not None:
        found_enrollment = None

        for enrollment in Enrollment.objects.all():
            if raw_identifier in (enrollment.current_raw_identifier(), enrollment.assigned_identifier,):
                found_enrollment = enrollment

                break

        if found_enrollment is None:
            found_enrollment = Enrollment(enrolled=now, last_fetched=now)

            found_enrollment.assign_random_identifier(raw_identifier)
            found_enrollment.save()
        else:
            found_enrollment.last_fetched = now
            found_enrollment.save()

        payload['identifier'] = found_enrollment.assigned_identifier

        payload['rules'] = {
            'rules': [],
            'additional-css': [],
            'actions': {},
        }

        if found_enrollment.rule_set is None:
            selected_rules = ExtensionRuleSet.objects.filter(is_default=True).first()

            if selected_rules is not None:
                found_enrollment.rule_set = selected_rules
                found_enrollment.save()

        if found_enrollment.rule_set is not None and found_enrollment.rule_set.is_active:
            payload['rules'] = found_enrollment.rule_set.rules()

            tasks = []

            now = timezone.now()

            for task in found_enrollment.tasks.filter(completed=None, active__lte=now).order_by('active'):
                tasks.append({
                    'message': task.task,
                    "url": task.url
                })

            payload['rules']['tasks'] = tasks
        else:
            payload['error'] = 'Participant not configured with ruleset and no default ruleset selected.'
    else:
        payload['error'] = 'Unable to retrieve original raw identifier from the request. Please fix and try again.'

    return HttpResponse(json.dumps(payload, indent=2), content_type='application/json', status=200)

@csrf_exempt
def uninstall(request): # pylint: disable=too-many-branches
    raw_identifier = request.POST.get('identifier', request.GET.get('identifier', None))

    now = timezone.now()

    if raw_identifier is not None:
        found_enrollment = None

        for enrollment in Enrollment.objects.all():
            if raw_identifier in (enrollment.current_raw_identifier(), enrollment.assigned_identifier,):
                found_enrollment = enrollment

                break

        if found_enrollment is not None:
            found_enrollment.last_uninstalled = now
            found_enrollment.save()

            return render(request, 'cookie_uninstall.html')

    raise Http404

@csrf_exempt
def privacy(request): # pylint: disable=too-many-branches
    return render(request, 'cookie_privacy.html')

@staff_member_required
def enrollments(request):
    context = {
        'enrollments': Enrollment.objects.all().order_by('-enrolled'),
        'groups': EnrollmentGroup.objects.all().order_by('name'),
    }

    return render(request, 'cookie_enrollments.html', context=context)

def unsubscribe_reminders(request, identifier):
    context = {}

    later = timezone.now() + datetime.timedelta(days=(365 * 250))

    Enrollment.objects.filter(assigned_identifier=identifier).update(contact_after=later)

    return render(request, 'cookie_unsubscribe_reminders.html', context=context)

def update_group(request):
    payload = {
        'message': 'Group not updated.'
    }

    if request.method == 'POST':
        identifier = request.POST.get('identifier', None)
        group = request.POST.get('group', None)

        enrollment = Enrollment.objects.filter(assigned_identifier=identifier).first()
        group = EnrollmentGroup.objects.filter(name=group).first()

        if enrollment is not None:
            enrollment.group = group
            enrollment.save()

            payload['message'] = 'New group for %s: %s' % (enrollment, group)

    return HttpResponse(json.dumps(payload, indent=2), content_type='application/json', status=200)
