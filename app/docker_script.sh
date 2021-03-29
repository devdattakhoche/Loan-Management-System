#!/bin/bash


python app/manage.py db init
python app/manage.py recreate db
python app/manage.py db migrate
python app/manage.py db upgrade
python app/manage.py runserver