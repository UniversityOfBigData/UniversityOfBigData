docker run -it --rm --entrypoint='' --env-file=.env \
  --mount type=bind,source="$(pwd)"/script/GCP/trial_universityofbigdata,target=/opt/universityofbigdata universityofbigdata python manage.py test $@
