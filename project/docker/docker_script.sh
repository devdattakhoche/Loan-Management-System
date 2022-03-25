#!/bin/bash


python manage.py db init
python manage.py recreate_db
python manage.py db migrate
python manage.py db upgrade
python manage.py runserver -h 0.0.0.0 -p 5000 -d
