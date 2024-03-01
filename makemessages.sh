docker run -it --rm --entrypoint='' --env-file=.env \
  -e DJANGO_SECRET_KEY='django-insecure-test-secret-key' \
  -e SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='google-oauth2-test-key' \
  -e SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='google-oauth2-test-secret' \
  --mount type=bind,source="$(pwd)"/universityofbigdata,target=/opt/universityofbigdata/universityofbigdata \
  --mount type=bind,source="$(pwd)"/apps,target=/opt/universityofbigdata/universityofbigdata/apps \
  --mount type=bind,source="$(pwd)"/locale,target=/opt/universityofbigdata/locale \
  universityofbigdata/universityofbigdata:latest bash -c "python manage.py makemessages -a"
