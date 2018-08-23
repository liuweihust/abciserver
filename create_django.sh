#!/bin/sh

ProjName="abciweb"
AppName="user"

rm -rf $ProjName
django-admin.py startproject $ProjName
cd $ProjName
django-admin.py startapp $AppName


python3 manage.py makemigrations
python3 manage.py migrate

python3  manage.py runserver 0.0.0.0:8000
