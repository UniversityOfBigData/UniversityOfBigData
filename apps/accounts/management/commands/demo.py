"""デモ用コマンド."""

import logging
from typing import List
import random
import time
from datetime import timedelta
from threading import Thread
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from random_word import RandomWords

import numpy as np
import shutil

from accounts.models import TeamTag
from competitions.models import (
        CompetitionModel, CompetitionPost
        )
from discussion.models import (
        Discussion, DiscussionPost,
        )
from competitions.management.commands.runapscheduler import setplan01
from universityofbigdata.settings import BASE_DIR


logger = logging.getLogger(__name__)
User = get_user_model()

SAMPLE_SIZE = 1000
NUM_CLASSES = 10


class AgentThread(Thread):

    def __init__(
            self, user_name='demo_user', seed=0,
            min_sleep=1, max_sleep=10,
            **kwargs):
        self.user_name = user_name

        # if self.user_name in (user.username for user in User.objects.all()):
        if len(User.objects.filter(username=self.user_name)) == 0:
            if len(TeamTag.objects.filter(name=self.user_name)) == 0:
                team = TeamTag.objects.create(name=self.user_name)
                team.save()
            else:
                team = TeamTag.objects.get(name=self.user_name)
            self.user = User.objects.create(
                    username=self.user_name,
                    nickname=f'{self.user_name}_nickname',
                    email=f'{self.user_name}@example.com',
                    # password=f'{self.user_name}_password',
                    selectedTeam=team,
                    **kwargs,
                    )
            self.user.save()
        else:
            self.user = User.objects.get(username=self.user_name)

        if self.user.is_staff or self.user.is_superuser:
            self.pages = [
                    'top', 'participation_guide',
                    ]
            self.actions = [
                'access_page',
                'launch_competition',
                'submission',
                'new_topic',
                'comment',
                # 'invite_user', 'create_team',
                ]
        else:
            self.pages = [
                    'top', 'participation_guide',
                    ]
            self.actions = [
                'access_page',
                'submission',
                'new_topic',
                'comment',
                # 'invite_user', 'create_team',
                ]

        self.client = Client()

        self.seed = seed
        random.seed(self.seed)

        self.min_sleep = min_sleep
        self.max_sleep = max_sleep

        self.r = RandomWords()

        self.is_halt = False

        Thread.__init__(self)

    def halt(self):
        self.is_halt = True

    def choose_action(self):
        return random.choice(self.actions)

    def execute_action(self, action):
        if (len(CompetitionModel.objects.all()) == 0) \
                and (self.user.is_staff or self.user.is_superuser):
            response = self.launch_competition(
                    title='__demo__' + self.random_words(10),
                    abstract=self.random_words(20, period=True),
                    description=self.random_words(50, period=True),
                    file_description=self.random_words(20, period=True),
                    problem_type=random.choice([
                        'classification', 'regression']),
                    public=random.choice([True, False]),
                    )
            return

        if action == 'access_page':
            self.client.get(reverse(random.choice(self.pages)))
        elif action == 'launch_competition':
            response = self.launch_competition(
                    title='__demo__' + self.random_words(10),
                    abstract=self.random_words(20, period=True),
                    description=self.random_words(50, period=True),
                    file_description=self.random_words(20, period=True),
                    problem_type=random.choice([
                        'classification', 'regression']),
                    public=random.choice([True, False]),
                    )
        elif action == 'new_topic':
            if len(CompetitionModel.objects.filter(status='active')) == 0:
                return
            comp = random.choice(CompetitionModel.objects.filter(
                status='active'))
            response = self.client.post(
                    reverse(
                        'Discussion:discussion_competition', args=[comp.id]),
                    {
                        'title_disc': '__demo__' + self.random_words(5),
                        'comment_field_disc': self.random_words(
                            30, period=True),
                    })
        elif action == 'comment':
            if (Discussion.objects.all()) == 0:
                return
            try:
                topic = random.choice(Discussion.objects.all())
            except IndexError:
                return
            response = self.client.post(
                    reverse(
                        'Discussion:discussion_post', args=[topic.id]),
                    {
                        'comment_field_post': self.random_words(
                            30, period=True),
                    })
        elif action == 'submission':
            if len(CompetitionModel.objects.filter(status='active')) == 0:
                return
            comp = random.choice(CompetitionModel.objects.filter(
                status='active'))

            if comp.problem_type == 'classification':
                pred = np.random.randint(
                        NUM_CLASSES, size=SAMPLE_SIZE, dtype=np.int)
            else:
                pred = np.random.rand(SAMPLE_SIZE)

            submission_file = SimpleUploadedFile(
                "pred.csv",
                "\n".join([
                    f'{v}' for i, v in enumerate(pred)
                    ]).encode()
            )

            try:
                response = self.client.post(
                    reverse('Competitions:competitions_post', args=[comp.id]),
                    {
                        'post_key': submission_file,
                        'count_par_today': 0,
                    })
            except RuntimeError as e:
                if str(e) == 'Invalid sample size':
                    pass
                else:
                    raise(e)

    def random_words(self, num_words, period=False):
        return ' '.join([
            self.r.get_random_word() for _ in range(num_words)
            ]) + ('.' if period else '')

    def run(self):
        logger.info(f'My name is {self.user_name}, running on {self.name}')
        self.client.force_login(self.user)
        """
        self.client.login(
                username=self.user.username,
                password=self.user.password)
        """

        while True:
            action = self.choose_action()
            self.execute_action(action)
            time.sleep(random.randrange(self.min_sleep, self.max_sleep))
            if self.is_halt:
                raise Exception('Receive request to halt')

    def launch_competition(
            self, title='', abstract='', description='',
            problem_type='classification',
            file_description='',
            leaderboard_type='default',
            n_max_submissions_per_day=3,
            public_leaderboard_percentage=50,
            public=True,
            ):
        open_datetime = timezone.make_aware(
            timezone.datetime.now() + timedelta(
                minutes=np.random.randint(1)))
        close_datetime = open_datetime + timedelta(
                minutes=np.random.randint(2) + 1)
        # 提出例ファイル
        if problem_type == 'classification':
            pred = np.random.randint(NUM_CLASSES, size=SAMPLE_SIZE, dtype=np.int)
            gt = np.random.randint(NUM_CLASSES, size=SAMPLE_SIZE, dtype=np.int)
            evaluation_type='accuracy'
        else:
            pred = np.random.rand(SAMPLE_SIZE)
            gt = np.random.rand(SAMPLE_SIZE)
            evaluation_type='mean_squared_error'
        pred_file = SimpleUploadedFile(
            "example_pred.csv",
            "\n".join([
                    f'{v}' for i, v in enumerate(pred)
                    ]).encode()
        )
        # 正解ファイル
        gt_file = SimpleUploadedFile(
            "gt.csv",
            "\n".join([
                    f'{v}' for i, v in enumerate(gt)
                    ]).encode()
        )

        response = self.client.post(
                reverse('competitions_create'),
                {
                    'title': title, 'title_en': title,
                    'competition_abstract': abstract,
                    'competition_description': description,
                    'problem_type': problem_type,
                    'evaluation_type': evaluation_type,
                    'file_description': file_description,
                    'blob_key': pred_file,
                    'truth_blob_key': gt_file,
                    'open_datetime': open_datetime,
                    'close_datetime': close_datetime,
                    'leaderboard_type': leaderboard_type,
                    'n_max_submissions_per_day': n_max_submissions_per_day,
                    'public_leaderboard_percentage': public_leaderboard_percentage,
                    'public': public,
                },
                )
        setplan01()
        return response


def create_users(num_users: int, prefix='demo_user', **kwargs) -> List[User]:
    existing_names = [user.username for user in User.objects.all()]
    names = [f'{prefix}{i}' for i in range(num_users)]
    return [
            User.objects.create(
                username=name,
                nickname=f'{name}_nickname',
                email=f'{name}@example.com',
                **kwargs,
                ) if name not in existing_names
            else User.objects.get(username=name)
            for name in names
            ]


class Command(BaseCommand):
    help = "Runs agents for demonstration."

    option_keys = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--num-users',
            action='store',
            dest='num_users',
            type=int,
            default=15,
            help='number of users',
            )
        parser.add_argument(
            '--num-staff-users',
            action='store',
            dest='num_staff_users',
            type=int,
            default=2,
            help='number of staff users',
            )
        parser.add_argument(
            '--num-super-users',
            action='store',
            dest='num_super_users',
            type=int,
            default=1,
            help='number of staff users',
            )

    def handle(self, *args, **options):
        # clean_data()
        logger.info("Creating users...")
        users = [AgentThread(
            user_name=f'__demo__user{i}', is_superuser=False, is_staff=False, is_participant=True,
            min_sleep=1, max_sleep=10,
            ) for i in range(options['num_users'])]
        staff_users = [AgentThread(
            user_name=f'__demo__staff_user{i}', is_superuser=False, is_staff=True, is_participant=True,
            min_sleep=1, max_sleep=5,
            ) for i in range(options['num_staff_users'])]
        super_users = [AgentThread(
            user_name=f'__demo__super_user{i}', is_superuser=True, is_staff=True, is_participant=True,
            min_sleep=1, max_sleep=5,
            ) for i in range(options['num_super_users'])]
        all_users = users + staff_users + super_users

        try:
            logger.info("Starting demo...")
            for agent in all_users:
                agent.start()
            for agent in all_users:
                agent.join()

        except KeyboardInterrupt:
            logger.info("Stopping demo...")
            for agent in all_users:
                # agent.terminate()
                agent.halt()
            for agent in all_users:
                agent.join()
            # demo.shutdown()
            logger.info("Demo shut down successfully!")
            clean_data()


def clean_data():
    for comp in CompetitionModel.objects.all():
        if comp.title.startswith('__demo__'):
            CompetitionPost.objects.filter(post=comp).delete()
            shutil.rmtree(
                    BASE_DIR / 'data' / 'media' / 'competition' / str(comp.uuid),
                    ignore_errors=True)
            comp.delete()
    for topic in Discussion.objects.all():
        if topic.title.startswith('__demo__'):
            DiscussionPost.objects.filter(post_tag_post=topic).delete()
            topic.delete()
    # NOTE: ユーザが消せないバグあり
    User.objects.filter(username__startswith='__demo__').all().delete()
    TeamTag.objects.filter(name__startswith='__demo__').all().delete()
