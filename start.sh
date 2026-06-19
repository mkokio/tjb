#!/bin/bash
python manage.py migrate --noinput
gunicorn --bind 0.0.0.0:8000 --workers 2 thejapanbike.wsgi