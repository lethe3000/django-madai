#!/bin/bash

git checkout master
git pull

pip install -r requirements/production.txt

cd src
#./manage.py mysql_utility -t
workon django-madai
./manage.py collectstatic --noinput --settings=settings.production
./manage.py syncdb --no-initial-data --settings=settings.production

./dbmigrate.sh production migrate
./dbmigrate.sh production convert
./dbmigrate.sh production fake

sudo /etc/init.d/httpd restart
