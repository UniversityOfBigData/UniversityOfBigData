"""コンペティションを作成するコマンド."""

from typing import Tuple, List
import logging
from argparse import ArgumentParser
from tempfile import TemporaryDirectory
from pathlib import Path
import shutil

from datasets import load_dataset
from tqdm import tqdm
from pytimeparse.timeparse import timeparse

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone
from django.test import Client
from django.contrib.auth import get_user_model

import pandas as pd
import numpy as np

from competitions.management.commands.runapscheduler import setplan01
from static.lib import metrics


logger = logging.getLogger(__name__)
User = get_user_model()

REPOSITORY_NAME = {
        'mnist': 'mnist',
        'titanic': 'lewtun/titanic',
        'iris': 'hitorilabs/iris',
        'wine': 'mstz/wine',
        'auto-mpg': 'scikit-learn/auto-mpg',
        }
COMPETITION_PARAMS = {
    'mnist': {
        'title': 'Digit Recognizer',
        'abstract': 'Image classification with MNIST, handwritten digit databese',
        'task': 'classification',
        'description': "The MNIST dataset consists of 70,000 28x28 black-and-white images of handwritten digits extracted from two NIST databases. There are 60,000 images in the training dataset and 10,000 images in the validation dataset, one class per digit so a total of 10 classes, with 7,000 images (6,000 train images and 1,000 test images) per class. Half of the image were drawn by Census Bureau employees and the other half by high school students (this split is evenly distributed in the training and testing sets).\n\nThis description was cited from https://huggingface.co/datasets/mnist/blob/main/README.md#dataset-summary.",
        'target_features': ['label'],
        },
    'titanic': {
        'title': 'Titanic - Machine Learning from Disaster',
        'abstract': 'Predict survival on the Titanic',
        'task': 'classification',
        'description':
        """The sinking of the Titanic is one of the most infamous shipwrecks in history.\n\n"""
        """On April 15, 1912, during her maiden voyage, the widely considered “unsinkable” RMS Titanic sank after colliding with an iceberg. Unfortunately, there weren’t enough lifeboats for everyone on board, resulting in the death of 1502 out of 2224 passengers and crew.\n\n"""
        """While there was some element of luck involved in surviving, it seems some groups of people were more likely to survive than others.\n\n"""
        """In this challenge, we ask you to build a predictive model that answers the question: “what sorts of people were more likely to survive?” using passenger data (ie name, age, gender, socio-economic class, etc).\n\n"""
        """This description was cited from https://www.kaggle.com/datasets/yasserh/titanic-dataset.""",
        'target_features': ['Survived'],
        },
    'iris': {
        'title': "Iris Species",
        'abstract': 'Classify iris plants into three species in the Iris dataset',
        'task': 'classification',
        'description': """The Iris dataset was used in R.A. Fisher's classic 1936 paper, The Use of Multiple Measurements in Taxonomic Problems, and can also be found on the UCI Machine Learning Repository.\n\n"""
        """It includes three iris species with 50 samples each as well as some properties about each flower. One flower species is linearly separable from the other two, but the other two are not linearly separable from each other.\n\n"""
        """The columns in this dataset are:\n\n"""
        """- Id\n"""
        """- SepalLengthCm\n"""
        """- SepalWidthCm\n"""
        """- PetalLengthCm\n"""
        """- PetalWidthCm\n"""
        """- Species\n\n"""
        """This description was cited from https://huggingface.co/datasets/hitorilabs/iris.""",
        'target_features': ['species'],
        },
    'wine': {
        'title': 'Wine Quality Data',
        'abstract': 'Predict quality and color from various chemical properties of wine',
        'task': 'classification',
        'description': """This data set contains various chemical properties of wine, such as acidity, sugar, pH, and alcohol. It also contains a quality metric (3-9, with highest being better) and a color (red or white).""",
        'target_features': ['quality', 'is_red'],
        },
    'auto-mpg': {
        'title': 'Auto Miles per Gallon (MPG)',
        'abstract': 'Predict Miles per Gallon (MPG) in various properties of cars',
        'task': 'regression',
        'description': '''This dataset is a slightly modified version of the dataset provided in the StatLib library. In line with the use by Ross Quinlan (1993) in predicting the attribute "mpg", 8 of the original instances were removed because they had unknown values for the "mpg" attribute. The original dataset is available in the file "auto-mpg.data-original".\n\n'''
        '''"The data concerns city-cycle fuel consumption in miles per gallon, to be predicted in terms of 3 multivalued discrete and 5 continuous attributes." (Quinlan, 1993)'''
        '''This description was cited from https://huggingface.co/datasets/scikit-learn/auto-mpg''',
        'target_features': ['mpg'],
        },
    'none': {
        'title': 'No title',
        'abstract': 'No abstract',
        'task': 'classification',
        'description': "No description.",
        'target_features': [],
        }
    }


class Command(BaseCommand):
    help = "Launch a new competition."

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            '--title',
            action='store',
            dest='title',
            type=str,
            default=None,
            help='title of the competition',
            )
        parser.add_argument(
            '--abstract',
            action='store',
            dest='abstract',
            type=str,
            default=None,
            help='abstract of the competition',
            )
        parser.add_argument(
            '--description',
            action='store',
            dest='description',
            type=str,
            default=None,
            help='description of the competition',
            )
        parser.add_argument(
            '--dataset',
            choices=[
                'mnist',
                'titanic',  # 'lewtun/titanic',
                'iris',  # 'hitorilabs/iris',
                'wine',  # 'mstz/wine',
                'auto-mpg',
                'none',
                ],
            default='none',
            dest='dataset',
            help='template of the dataset',
            )
        parser.add_argument(
            '--data',
            action='store',
            dest='data',
            type=str,
            default=None,
            help='path of training dataset',
            )
        parser.add_argument(
            '--gt-data',
            action='store',
            dest='gt_data',
            type=str,
            default=None,
            help='path of ground-truth data of test dataset',
            )
        parser.add_argument(
            '--user-name',
            action='store',
            dest='user_name',
            type=str,
            default='admin',
            help='name of user to launch the competition',
            )
        parser.add_argument(
            '--start-datetime',
            action='store',
            dest='start_datetime',
            type=str,
            default='0m',
            help="datetime for start of the competition, given in ISO 8601 format or pytimeparse format",
            )
        parser.add_argument(
            '--end-datetime',
            action='store',
            dest='end_datetime',
            type=str,
            default='10m',
            help="datetime for end of the competition, given in ISO 8601 format or pytimeparse format",
            )
        parser.add_argument(
            '--n-max-submissions-per-day',
            action='store',
            dest='n_max_submissions_per_day',
            type=int,
            default=3,
            help="maximum number of submissions in a day",
            )
        parser.add_argument(
            '--public-lb-percentage',
            action='store',
            dest='public_lb_percentage',
            type=float,
            default=50.,
            help="percentage of public LB data",
            )
        parser.add_argument(
            '--task',
            choices=[
                'classification',
                'regression',
                ],
            default=None,
            dest='task',
            help="task of the competition, 'classification' or 'regression'",
            )
        parser.add_argument(
            '--metric',
            choices=list(metrics.keys()),
            default='accuracy',
            dest='metric',
            help="metric of the competition",
            )
        parser.add_argument(
            '--private',
            default=True,
            dest='public',
            action='store_false',
            help="flag the competition as private",
            )
        parser.add_argument(
            '--test-size',
            action='store',
            dest='test_size',
            type=float,
            default=0.3,
            help="fraction of test data, used if test split does not exist",
            )

    def handle(self, *args, **options):
        self.client = Client()
        self.user = User.objects.get(username=options['user_name'])
        self.client.force_login(self.user)

        start_datetime = parse_datetime_str(options['start_datetime'])
        end_datetime = parse_datetime_str(options['end_datetime'])

        dataset_name = options['dataset']
        if dataset_name != 'none':
            temp_dir = TemporaryDirectory()
            data_path, gt_path = download_dataset(
                    REPOSITORY_NAME[dataset_name],
                    target_features=COMPETITION_PARAMS[
                        dataset_name]['target_features'],
                    dst_dir=temp_dir.name)
            params = COMPETITION_PARAMS[dataset_name]
        else:
            data_path = options['data_data']
            gt_path = options['gt_data']
            params = COMPETITION_PARAMS[dataset_name]

        for key in ['title', 'abstract', 'description', 'task']:
            if options[key] is not None:
                params[key] = options[key]

        self.launch_competition(
                data_path=data_path,
                gt_path=gt_path,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                n_max_submissions_per_day=options['n_max_submissions_per_day'],
                public_lb_percentage=options['public_lb_percentage'],
                public=options['public'],
                test_size=options['test_size'],
                **params
                )

    def launch_competition(
            self,
            data_path: str,
            gt_path: str,
            start_datetime: datetime,
            end_datetime: datetime,
            title='mnist',
            abstract='Competition with mnist dataset',
            description='Competition with mnist dataset',
            task='classification',
            metrics='accuracy',
            file_description='train data',
            leaderboard_type='default',
            n_max_submissions_per_day=3,
            public_lb_percentage=50,
            public=True,
            *args, **kwargs,
            ):

        data_file = open(data_path, 'rb')
        gt_file = open(gt_path, 'rb')

        response = self.client.post(
                reverse('competitions_create'),
                {
                    'title': title, 'title_en': title,
                    'competition_abstract': abstract,
                    'competition_description': description,
                    'problem_type': task,
                    'evaluation_type': metrics,
                    'file_description': file_description,
                    'blob_key': data_file,
                    'truth_blob_key': gt_file,
                    'open_datetime': start_datetime,
                    'close_datetime': end_datetime,
                    'leaderboard_type': leaderboard_type,
                    'n_max_submissions_per_day': n_max_submissions_per_day,
                    'public_leaderboard_percentage': public_lb_percentage,
                    'public': public,
                },
                )
        setplan01()

        data_file.close()
        gt_file.close()

        return response


def parse_datetime_str(dt_str: str) -> datetime:
    try:
        dt = timezone.make_aware(datetime.fromisoformat(dt_str))
    except ValueError:
        dt = timezone.make_aware(
                timezone.datetime.now() + timedelta(
                    seconds=timeparse(dt_str)))
    return dt


def download_dataset(
        dataset_name: str,
        target_features: List[str],
        dst_dir: str,
        test_size: float = 0.3,
        ) -> Tuple[str]:
    """Download a dataset."""
    # download hf dataset
    logger.info(f'Downloading {dataset_name}...')
    dataset = load_dataset(dataset_name)
    logger.info('Finished downloading')

    # split train/test if test does not exist
    if 'test' not in dataset.keys():
        dataset = dataset['train'].train_test_split(test_size=test_size)

    # prepare directories

    data_dir = Path(dst_dir) / 'data'
    data_dir.mkdir()

    if dataset_name != 'mnist':
        train_df = dataset['train'].to_pandas()
        test_df = dataset['test'].to_pandas()
        train_df.to_csv(data_dir / 'train.csv', index=False)
        test_df.drop(columns=target_features).to_csv(
                data_dir / 'test.csv', index=False)

        # archive data dir
        zip_path = shutil.make_archive('data.zip', 'zip', str(data_dir))

        # gt data
        gt_path = Path(dst_dir) / 'test_labels.csv'
        test_df.loc[:, target_features].to_csv(
                gt_path, header=None, index=False)
    else:
        train_dir = data_dir / 'train'
        train_dir.mkdir()

        test_dir = data_dir / 'test'
        test_dir.mkdir()

        train_size = dataset['train'].num_rows
        test_size = dataset['test'].num_rows
        num_digits = np.ceil(np.log10(train_size + test_size)).astype(int)

        # make label dirs
        for label in dataset['train'].info.features['label'].names:
            (train_dir / label).mkdir()
        # save images
        logger.info(f'Saving images...')
        for i, img in enumerate(tqdm(
                dataset['train']['image'], desc='save images')):
            label = dataset['train']['label'][i]
            img.save(train_dir / str(label) / f'{str(i).zfill(num_digits)}.png')

        for i, img in enumerate(dataset['test']['image']):
            img.save(test_dir / f'{str(i).zfill(num_digits)}.png')

        # save train labels
        pd.DataFrame({'label': dataset['train']['label']}).to_csv(
                train_dir / 'train_labels.csv', header=None, index=False)

        # archive data dir
        zip_path = shutil.make_archive('data.zip', 'zip', str(data_dir))

        # gt data
        gt_path = Path(dst_dir) / 'test_labels.csv'
        pd.DataFrame({'label': dataset['test']['label']}).to_csv(
                gt_path, header=None, index=False)

    return zip_path, gt_path
