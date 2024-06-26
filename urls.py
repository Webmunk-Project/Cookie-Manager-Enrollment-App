# pylint: disable=line-too-long

from django.conf.urls import url

from .views import enroll, uninstall, enrollments, unsubscribe_reminders, update_group, privacy

urlpatterns = [
    url(r'^enroll.json$', enroll, name='enroll'),
    url(r'^uninstall$', uninstall, name='uninstall'),
    url(r'^privacy$', privacy, name='privacy'),
    url(r'^unsubscribe/(?P<identifier>.+)$', unsubscribe_reminders, name='unsubscribe_reminders'),
    url(r'^enrollments$', enrollments, name='enrollments'),
    url(r'^update_group.json$', update_group, name='update_group'),
]
