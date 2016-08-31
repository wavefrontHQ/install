#!/bin/bash

#-------------------------------------------------------------
# Apache Init
#-------------------------------------------------------------
service apache2 start


#-------------------------------------------------------------
# Postgresql Init
#-------------------------------------------------------------
service postgresql start

# initialize the database and link the database to
# the test user docker
su -c "cat /tmp/init.sql | psql -a" - postgres


#-------------------------------------------------------------
# Redis Init
#-------------------------------------------------------------
# instructions from redis.io/download
wget http://download.redis.io/releases/redis-3.2.3.tar.gz
tar xzf redis-3.2.3.tar.gz
cd redis-3.2.3
make
./src/redis-server &
cd ..
