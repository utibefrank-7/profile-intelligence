release: python manage.py migrate
web: gunicorn IntelligentProfile.wsgi:application --bind 0.0.0.0:$PORT