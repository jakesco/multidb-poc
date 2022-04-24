#!/bin/bash

DBS="default tenant1 tenant2"

rm *.sqlite3

for db in $DBS; do
  python manage.py migrate --database=$db
done

python manage.py loaddata fixtures.json
