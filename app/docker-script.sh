python manage.py init
python manage.py migrate
python manage.py upgrade
/usr/local/bin/gunicorn -w 2 -b :8000 wsgi:app