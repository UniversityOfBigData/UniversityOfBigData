#!/bin/bash

docker run -it --rm \
  -v "$(pwd)/uwsgi/uwsgi.ini:/opt/universityofbigdata/uwsgi.ini" \
  -v "$(pwd)/data:/opt/universityofbigdata/data" \
  -v "$(pwd)/initialize_in_container.sh:/opt/universityofbigdata/initialize_in_container.sh" \
  --entrypoint='' \
  universityofbigdata/universityofbigdata:latest /bin/bash ./initialize_in_container.sh
