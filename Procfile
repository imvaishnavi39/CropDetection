release: python manage.py migrate && python manage.py collectstatic --no-input
web: gunicorn Crop.wsgi:application --bind 0.0.0.0:$PORT
