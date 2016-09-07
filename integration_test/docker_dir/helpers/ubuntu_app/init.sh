#!/bin/bash

#-------------------------------------------------------------
# Apache Init
#-------------------------------------------------------------
service apache2 start


#-------------------------------------------------------------
# Cassandra Init
#-------------------------------------------------------------
service cassandra start


#-------------------------------------------------------------
# Memcached Init
#-------------------------------------------------------------
memcached-1.4.31/memcached -u root -d

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
./redis-3.2.3/src/redis-server &


#-------------------------------------------------------------
# Zookeeper Init
#-------------------------------------------------------------
# install zookeeper
./zookeeper-3.4.8/bin/zkServer.sh start &
