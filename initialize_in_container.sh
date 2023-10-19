#!/bin/bash

mkdir -p data/static data/media data/log/nginx

echo \"Running database migrations...\"
python manage.py makemigrations accounts
python manage.py makemigrations authentication
python manage.py makemigrations management
python manage.py makemigrations competitions
python manage.py makemigrations universityofbigdata
python manage.py makemigrations discussion
python manage.py makemigrations userlog
python manage.py makemigrations
python manage.py migrate

# 管理者ユーザの作成
python manage.py createsuperuser $@

# 初期設定
python manage.py shell < setup_temp.py
