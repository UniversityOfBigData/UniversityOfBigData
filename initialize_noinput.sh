#!/bin/bash

docker run \
  -v "$(pwd)/uwsgi/uwsgi.ini:/opt/universityofbigdata/uwsgi.ini" \
  -v "$(pwd)/data:/opt/universityofbigdata/data" \
  -v "$(pwd)/initialize_in_container.sh:/opt/universityofbigdata/initialize_in_container.sh" \
  --entrypoint='' \
  -e DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD} \
  -e DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME} \
  -e DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL} \
  universityofbigdata/universityofbigdata:latest /bin/bash ./initialize_in_container.sh --noinput
