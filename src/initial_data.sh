#!/bin/bash
rm default.db
./manage.py syncdb --no-initial-data --settings=settings.local
./manage.py loaddata initial_data.json --settings=settings.local
./manage.py loaddata mock_data.json --settings=settings.local
./manage.py loaddata test_customer_data.json --settings=settings.local

