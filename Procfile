web: gunicorn core.wsgi

# Uncomment this `release` process if you are using a database, so that Django's model
# migrations are run as part of app deployment, using Heroku's Release Phase feature:
# https://docs.djangoproject.com/en/4.2/topics/migrations/
# https://devcenter.heroku.com/articles/release-phase
echo ${GOOGLE_CREDENTIALS} > /app/google-credentials.json

release: ./manage.py migrate --no-input && ./manage.py fake_date && python create_google_storage_file.py
