#!/bin/bash
service postgresql start
if [ $? -ne 0 ]; then
    echo "Failed to start postgresql service."
fi

# initialize the database and link the database to
# the test user docker
su -c "cat /tmp/init.sql | psql -a" - postgres
