"""コンペティションの状態を更新するスケジューラを実行するコマンド."""

import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler  # 定期実行処理用
from competitions.models import CompetitionModel  # コンペ管理用
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler import util

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from django.utils import timezone  # ローカルタイム管理
from django.utils.timezone import localtime  # ローカルタイム管理用


logger = logging.getLogger(__name__)


def setplan01():
    choices=[
            ('coming', _('開催準備中')),
            ('active', _('開催中')),
            ('completed', _('開催終了')),
            ]
    logger.info("Running 'setplan01'.")
    status = 'coming'
    compALL = CompetitionModel.objects.all()
    now_time = localtime(timezone.now())
    for comp in compALL:
        open_date =comp.open_datetime
        close_date=comp.close_datetime
        word = ''
        if(now_time < open_date):
            status = 'coming'
            # 開催
            word = _('コンペティション') +' ' + comp.title + ' '+ _('開催準備中です。')
        elif((now_time > close_date)):
            status = 'completed'
            # 終了ログ発出
            """
            # FIXME: winner_teamsを更新してから取得する必要がある
            winner_t = ''
            winners_sets =comp.winner_teams.all()
            for winner in winners_sets:
                winner_t = winner_t + winner.name + ' '
            """
            word = _('コンペティション')+' ' + comp.title + ' ' + _('が終了しました。')
            # + '\n'+ _('優勝者チームは')+ ' ' + winner_t + ' '+ _('です。')
        else:
            status = 'active'
            # 開始ログ発出
            word = _('コンペティション')+ ' ' + comp.title + ' '+ _('が始まりました。')

        if (comp.status != status):
            # 変更があった場合、ログ出力
            logger.info(word, extra={'competition_id': comp.id})

        comp.status = status
        comp.save()
        # print( now_time, comp.title ,now_time, status  )


# Adapted from: https://pypi.org/project/django-apscheduler/
# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way. 
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler for updating states of competitions."

    option_keys = [
            'year', 'month', 'day', 'week', 'day_of_week', 'hour',
            'minute', 'second'
        ]

    def add_arguments(self, parser):
        for t in self.option_keys:
            parser.add_argument(
                    '--' + t, default="*", type=str, required=False)

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
                setplan01,
                trigger=CronTrigger(
                    **{k: options[k] for k in self.option_keys}
                ),
                id='setplan01',
                max_instances=1,
                replace_existing=True,
        )
        logger.info("Added job 'setplan01'.")

        scheduler.add_job(
                delete_old_job_executions,
                trigger=CronTrigger(
                    day_of_week="mon", hour="00", minute="00"
                ),
                id="delete_old_job_executions",
                max_instances=1,
                replace_existing=True,
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
