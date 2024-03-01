#!/bin/bash

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Making migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations authentication
python manage.py makemigrations management
python manage.py makemigrations competitions
python manage.py makemigrations discussion

echo "Running database migrations..."
python manage.py migrate

echo "Initialize the DB if not yet initialized..."
python manage.py initialize_db

echo "Starting scheduler..."
python manage.py runapscheduler --minute "*/10" --second "0" &

echo "Creating a superuser..."
python manage.py createsuperuser --noinput

echo "Starting server..."
uwsgi --ini /opt/universityofbigdata/uwsgi.ini
