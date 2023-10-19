#!/bin/bash

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting scheduler..."
python manage.py runapscheduler --hour "*/1"

echo "Starting server..."
uwsgi --ini /opt/universityofbigdata/uwsgi.ini
