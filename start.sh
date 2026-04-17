#!/bin/bash
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn IntelligentProfile.wsgi:application --bind 0.0.0.0:8080
