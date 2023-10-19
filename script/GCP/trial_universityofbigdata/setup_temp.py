#!/usr/bin/env python
"""Django's DB"""
#
from accounts.models import TeamTag
TeamTag.objects.create(name='InitialTeam000')
#
from management.models import ConfigBox
ConfigBox.objects.create(name='signInCode')
#
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
# make group
permlist=[
Permission.objects.get(codename="add_teamtag"),
Permission.objects.get(codename="change_teamtag"),
Permission.objects.get(codename="view_teamtag"),
Permission.objects.get(codename="change_user"),
Permission.objects.get(codename="view_user"),
Permission.objects.get(codename="add_competitionmodel"),
Permission.objects.get(codename="change_competitionmodel"),
Permission.objects.get(codename="view_competitionmodel"),
Permission.objects.get(codename="add_competitionpost"),
Permission.objects.get(codename="change_competitionpost"),
Permission.objects.get(codename="view_competitionpost"),
Permission.objects.get(codename="change_configbox"),
Permission.objects.get(codename="view_configbox"),
]
Group.objects.create(name='TA')
ta_group = Group.objects.get(name='TA')
ta_group.permissions.set(permlist)
#
permlist_p=[
Permission.objects.get(codename="view_teamtag"),
Permission.objects.get(codename="view_competitionmodel"),
Permission.objects.get(codename="add_competitionpost"),
Permission.objects.get(codename="change_competitionpost"),
Permission.objects.get(codename="view_competitionpost"),
Permission.objects.get(codename="view_configbox"),
]
Group.objects.create(name='Participant')
part_group = Group.objects.get(name='Participant')
part_group.permissions.set(permlist_p)
