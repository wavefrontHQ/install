#!/bin/bash
service mysql start

# initialize the database and link the database to
# the test user docker
cat init.sql | mysql -u root --password=root
