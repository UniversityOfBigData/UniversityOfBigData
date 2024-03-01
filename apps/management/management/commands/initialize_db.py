"""データベース初期化コマンド."""

import logging

from django.core.management.base import BaseCommand

from accounts.models import TeamTag
from management.models import ConfigBox
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Initialize the database for universityofbigdata."

    def handle(self, *args, **options) -> None:
        # 初期チームの作成
        if len(TeamTag.objects.filter(name='InitialTeam000')) == 0:
            TeamTag.objects.create(name='InitialTeam000')

        # ConfigBoxの作成
        if len(ConfigBox.objects.all()) == 0:
            ConfigBox.objects.create()

        # TAグループの作成
        if len(Group.objects.filter(name='TA')) == 0:
            Group.objects.create(name='TA').permissions.set([
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
                ])

        # 参加者グループの作成
        if len(Group.objects.filter(name='Participant')) == 0:
            Group.objects.create(name='Participant').permissions.set([
                Permission.objects.get(codename="view_teamtag"),
                Permission.objects.get(codename="view_competitionmodel"),
                Permission.objects.get(codename="add_competitionpost"),
                Permission.objects.get(codename="change_competitionpost"),
                Permission.objects.get(codename="view_competitionpost"),
                Permission.objects.get(codename="view_configbox"),
                ])
