#!/bin/bash

#-------------------------------------------------------------
# Apache Init
#-------------------------------------------------------------
service apache2 start


#-------------------------------------------------------------
# MySQL Init
#-------------------------------------------------------------
service mysql start

# initialize the database and link the database to
# the test user docker
cat /tmp/mysql/init.sql | mysql -u root --password=root


#-------------------------------------------------------------
# Nginx Init
#-------------------------------------------------------------
service nginx start


#-------------------------------------------------------------
# Postgresql Init
#-------------------------------------------------------------
service postgresql start

# initialize the database and link the database to
# the test user docker
su -c "cat /tmp/postgresql/init.sql | psql -a" - postgres


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


#-------------------------------------------------------------
# Cassandra Init
#-------------------------------------------------------------
service cassandra start
