#!/bin/bash
service postgresql start

# initialize the database and link the database to
# the test user docker
su -c "cat /tmp/init.sql | psql -a" - postgres
