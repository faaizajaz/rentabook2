web: gunicorn rentabook2.wsgi:application --timeout 500
release: python manage.py makemigrations; python manage.py migrate --noinput; python manage.py loaddata bookcount.json
