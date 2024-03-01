import datetime
from django.utils import timezone

from competitions.models import CompetitionPost


def count_daily_submissions(user, competition):
    today = timezone.localtime(timezone.now()).date()
    today = timezone.datetime(
            today.year, today.month, today.day,
            tzinfo=timezone.get_current_timezone())
    tomorrow = (today + datetime.timedelta(days=1))
    query_set = CompetitionPost.objects.filter(
            post=competition, team_tag=user.selectedTeam,
            added_datetime__range=[today, tomorrow])
    return len(query_set)
